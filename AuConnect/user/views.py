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

        # Doğrulama kodunu mail olarak gönder
        try:
            send_mail(
                'Ankara Üniversitesi Mail Doğrulama',
                f'Doğrulama kodunuz: {verification_code}\n\nİletişim : auconnectverify@gmail.com\nBir sorunla karşılaştığınızda bizle iletişime geçiniz...',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            
            return JsonResponse({
                "success": True,
                "message": "Doğrulama kodu email adresinize gönderildi."
            })
        except Exception as e:
            # Hata durumunda hata mesajını log'a yazdır ve kullanıcıya bildir
            print(f"Email gönderme hatası: {str(e)}")
            return JsonResponse({
                "success": False,
                "message": f"Email gönderilirken bir hata oluştu. Lütfen sistem yöneticisiyle iletişime geçin. Hata detayı: {str(e)}"
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