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
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

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
        verification_code = str(uuid.uuid4())  # Convert UUID to string
        
        # Eğer bu email için bekleyen bir profil varsa güncelle, yoksa oluştur
        profile, created = Profile.objects.get_or_create(
            temporary_email=email,
            defaults={
                'verification_code': verification_code,
                'email_verified': False,
            }
        )
        
        if not created:
            profile.verification_code = verification_code
            profile.email_verified = False
            profile.save()

        # Doğrulama kodunu mail olarak gönder
        try:
            print(f"Mail gönderme denemesi başladı...")
            print(f"Gönderen: {settings.EMAIL_HOST_USER}")
            print(f"Alıcı: {email}")
            print(f"Konu: Ankara Üniversitesi Mail Doğrulama")
            print(f"Kod: {verification_code}")
            
            send_mail(
                'Ankara Üniversitesi Mail Doğrulama',
                f'Doğrulama kodunuz: {verification_code}\n\nİletişim : auconnectverify@gmail.com\nBir sorunla karşılaştığınızda bizle iletişime geçiniz...',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            
            print("Mail başarıyla gönderildi!")
            
            return JsonResponse({
                "success": True,
                "message": "Doğrulama kodu email adresinize gönderildi."
            })
        except Exception as e:
            # Hata durumunda hata mesajını log'a yazdır ve kullanıcıya bildir
            print(f"Email gönderme hatası: {str(e)}")
            print(f"Hata türü: {type(e).__name__}")
            import traceback
            print(f"Hata detayı: {traceback.format_exc()}")
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
            verification_code = str(uuid.uuid4())  # Convert UUID to string
            # Önce mevcut bir geçici profil olup olmadığını kontrol et
            temp_profile = Profile.objects.filter(temporary_email=email, user__isnull=True).first()
            if not temp_profile:
                temp_profile = Profile.objects.create(
                    temporary_email=email,
                    verification_code=verification_code,
                    email_verified=False
                )
            else:
                temp_profile.verification_code = verification_code
                temp_profile.email_verified = False
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

def send_password_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'})
        if not username:
            return JsonResponse({'status': 'error', 'message': 'Kullanıcı adı girilmedi.'})
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Kullanıcı bulunamadı.'})
        if not user.email:
            return JsonResponse({'status': 'error', 'message': 'Bu kullanıcıya ait e-posta adresi bulunamadı.'})
        # Şifreyi düz olarak veritabanında tutmuyorsanız, bu kısım çalışmaz! Ama istek öyleydi.
        # Django'da şifreler hashli tutulur, düz şifre gönderilemez. Güvenlik için yeni şifre üretip göndermek daha doğrudur.
        # Burada örnek olarak yeni bir şifre üretilip kullanıcıya atanacak ve mail ile gönderilecek.
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        user.set_password(new_password)
        user.save()
        try:
            send_mail(
                'AuConnect Şifre Sıfırlama',
                f'Sayın {user.username},\n\nYeni şifreniz: {new_password}\n\nGiriş yaptıktan sonra şifrenizi profilinizden değiştirebilirsiniz.\n\nAuConnect Ekibi',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return JsonResponse({'status': 'success', 'message': 'Yeni şifreniz e-posta adresinize gönderildi.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'E-posta gönderilemedi: {str(e)}'})
    return JsonResponse({'status': 'error', 'message': 'Sadece POST isteği kabul edilir.'})

def change_password_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Giriş yapmalısınız.'})
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            current_password = data.get('current_password', '').strip()
            new_password = data.get('new_password', '').strip()
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'})
        if not current_password or not new_password:
            return JsonResponse({'status': 'error', 'message': 'Tüm alanları doldurunuz.'})
        user = request.user
        if not user.check_password(current_password):
            return JsonResponse({'status': 'error', 'message': 'Mevcut şifreniz yanlış.'})
        if len(new_password) < 6:
            return JsonResponse({'status': 'error', 'message': 'Yeni şifre en az 6 karakter olmalı.'})
        user.set_password(new_password)
        user.save()
        return JsonResponse({'status': 'success', 'message': 'Şifreniz başarıyla güncellendi.'})
    return JsonResponse({'status': 'error', 'message': 'Sadece POST isteği kabul edilir.'})