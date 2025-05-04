from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth, messages
from .models import Profile
import random
import string
from django.core.mail import send_mail
from django.conf import settings
import uuid
from django.http import JsonResponse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def login(request):
    
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("anasayfa")
        else :
            messages.add_message(request, messages.ERROR, "Kullanıcı adı veya parola yanlış...")
            return redirect("login")
    else:
        return render(request, 'user/login.html')


def send_verification_code(request):
    if request.method == "POST":
        email = request.POST.get('email')
        
        # Email formatı kontrolü
        if not email.endswith("@ogrenci.ankara.edu.tr"):
            return JsonResponse({
                "success": False,
                "message": "Sadece @ogrenci.ankara.edu.tr uzantılı mail adresi kabul ediliyor."
            })
        
        # Email kayıtlı mı kontrolü
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                "success": False,
                "message": "Bu email adresi zaten kayıtlı."
            })
        
        # Doğrulama kodu oluştur
        verification_code = generate_verification_code()
        
        # Eğer bu email için bekleyen bir profil varsa güncelle, yoksa oluştur
        profile, created = Profile.objects.get_or_create(
            temporary_email=email,
            defaults={'verification_code': verification_code}
        )
        
        if not created:
            profile.verification_code = verification_code
            profile.save()
            
        print(f"Doğrulama kodu oluşturuldu: {verification_code} - Email: {email}")

        try:
            # Daha güvenli bir şekilde SMTP'yi doğrudan kullan
            print("SMTP bağlantısı kuruluyor...")
            
            # SMTP sunucusuna bağlan
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.ehlo()
            server.starttls()
            
            print("SMTP sunucusuna giriş yapılıyor...")
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            
            # Mail hazırla
            message = MIMEMultipart("alternative")
            message["Subject"] = "Ankara Üniversitesi Mail Doğrulama"
            message["From"] = settings.EMAIL_HOST_USER
            message["To"] = email
            
            # Mail içeriği
            text = f"""
            Ankara Üniversitesi Mail Doğrulama
            
            Doğrulama kodunuz: {verification_code}
            
            İletişim: auconnectverify@gmail.com
            Bir sorunla karşılaştığınızda bizle iletişime geçiniz...
            """
            
            # MIME Part'ı oluştur
            part = MIMEText(text, "plain")
            message.attach(part)
            
            print("Mail gönderiliyor...")
            # Maili gönder
            server.sendmail(settings.EMAIL_HOST_USER, [email], message.as_string())
            server.quit()
            
            print("Mail başarıyla gönderildi!")
            
            return JsonResponse({
                "success": True,
                "message": "Doğrulama kodu email adresinize gönderildi."
            })
            
        except Exception as e:
            # Hata durumunda hata mesajını log'a yazdır
            print(f"Email gönderme hatası: {str(e)}")
            print(f"Hata türü: {type(e).__name__}")
            print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
            print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
            print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
            
            # Kendimize test maili göndermeyi dene
            try:
                print("Test mail gönderiliyor...")
                
                # Test için SMTP sunucusuna bağlan
                test_server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                test_server.ehlo()
                test_server.starttls()
                test_server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                
                # Test mail hazırla
                test_message = MIMEMultipart("alternative")
                test_message["Subject"] = "AuConnect Test Mail"
                test_message["From"] = settings.EMAIL_HOST_USER
                test_message["To"] = settings.EMAIL_HOST_USER
                
                test_text = "Bu bir test mailidir. Mail sistemi çalışıyor ancak öğrenci mailine göndermede sorun var."
                test_part = MIMEText(test_text, "plain")
                test_message.attach(test_part)
                
                # Test maili gönder
                test_server.sendmail(settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], test_message.as_string())
                test_server.quit()
                
                print("Test mail başarıyla gönderildi!")
                
                # Hata var ama doğrulama kodunu döndürelim (DEV MODU)
                return JsonResponse({
                    "success": True,
                    "message": f"Şu anda mail gönderilemedi, ancak kayıt işlemine devam edebilirsiniz. Doğrulama kodunuz: {verification_code}"
                })
                
            except Exception as test_e:
                print(f"Test mail hatası: {str(test_e)}")
                return JsonResponse({
                    "success": False,
                    "message": f"Email gönderilirken bir hata oluştu: {str(e)}. Test mail de başarısız oldu: {str(test_e)}"
                })

    return JsonResponse({"success": False, "message": "Geçersiz istek."})


def register(request):
    if request.method == "POST": 
        email = request.POST["email"]
        if not email.endswith("@ogrenci.ankara.edu.tr"):
            messages.add_message(request, messages.WARNING, "Sadece @ogrenci.ankara.edu.tr uzantılı mail adresi kabul ediliyor.")
            return redirect('register')

        verification_code = request.POST.get("verification_code", "")
        
        # Eğer verification code varsa doğrula
        if verification_code:
            # Geçici profili bul
            temp_profile = Profile.objects.filter(temporary_email=email, user__isnull=True).first()
            
            if not temp_profile:
                messages.add_message(request, messages.WARNING, "Önce mail doğrulaması yapmalısınız.")
                return redirect('register')
                
            if str(temp_profile.verification_code) != verification_code:
                messages.add_message(request, messages.WARNING, "Doğrulama kodu hatalı.")
                return redirect('register')
        else:
            # Doğrulama kodu yoksa otomatik code oluştur ve devam et
            verification_code = str(generate_verification_code())
            # Önce mevcut bir geçici profil olup olmadığını kontrol et
            temp_profile = Profile.objects.filter(temporary_email=email, user__isnull=True).first()
            if not temp_profile:
                temp_profile = Profile.objects.create(
                    temporary_email=email,
                    verification_code=verification_code
                )
            else:
                temp_profile.verification_code = verification_code
                temp_profile.save()

        username = request.POST["username"]
        password = request.POST["password"]
        repassword = request.POST["repassword"]
        role = request.POST["role"]
        
        if password == repassword:
            if User.objects.filter(username=username).exists():
                messages.add_message(request, messages.WARNING, "Bu kullanıcı adı daha önce alınmış")
                return redirect('register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.add_message(request, messages.WARNING, "Bu email daha önce alınmış")
                    return redirect('register')
                else:
                    # Kullanıcı oluşturmadan önce geçici profili hazırla
                    if temp_profile:
                        temp_profile.role = role
                        temp_profile.email_verified = True
                        temp_profile.save()
                    
                    # Kullanıcı oluştur - bu aşamada signal otomatik olarak çalışacak ve
                    # ya mevcut geçici profili kullanıcıya bağlayacak ya da yeni profil oluşturacak
                    user = User.objects.create_user(username=username, password=password, email=email)
                    
                    # Otomatik login yapma işlemini de ekleyelim
                    auth.login(request, user)
                    
                    messages.add_message(request, messages.SUCCESS, "Kullanıcı oluşturuldu ve giriş yapıldı.")
                    return redirect('anasayfa')  # Anasayfaya yönlendir
        else:
            messages.add_message(request, messages.WARNING, "Parolalarınız eşleşmiyor")
            return redirect("register")
    else:
        return render(request, "user/register.html")
    

def logout(request):

    if request.method == "POST":
        auth.logout(request)
        return redirect('index')
    else:
        return render(request, "user/logout.html")


def generate_verification_code():
    return uuid.uuid4()  # UUID oluşturur ve geri döner