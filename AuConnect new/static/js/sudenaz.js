
// Sekme işlevselliği
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');

tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Aktif sekme düğmesini güncelle
        tabButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Aktif sekme içeriğini güncelle
        const tabId = button.getAttribute('data-tab');
        tabContents.forEach(content => content.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
    });
});

// Etkinlik Modal İşlevselliği
const modal = document.getElementById('eventModal');
const postCards = document.querySelectorAll('.post-card');
const closeModal = document.querySelector('.close-modal');

// Etkinlik kartlarına tıklama işlevselliği ekle
postCards.forEach(card => {
    card.addEventListener('click', () => {
        const eventId = card.getAttribute('data-event-id');
        openEventModal(eventId);
    });
});

// Modal kapatma
closeModal.addEventListener('click', () => {
    modal.style.display = 'none';
});

// Dışarı tıklayınca modal kapanır
window.addEventListener('click', (event) => {
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});

// Etkinlik detaylarını göster
function openEventModal(eventId) {
    // Bu fonksiyon daha sonra API'dan gerçek verileri alabilir
    // Şimdilik sabit veriler kullanıyoruz
    const eventData = {
        '1': {
            title: 'Yapay Zeka ve Etik Paneli',
            community: 'Yapay Zeka Topluluğu',
            communityImg: 'assets/community-icon.png',
            date: '15 Mayıs 2023',
            location: '100. Yıl Konferans Salonu',
            time: '14:00 - 16:30',
            image: 'assets/event1.jpg',
            description: 'Yapay zeka teknolojilerinin etik boyutlarını tartışacağımız bu panelde, alanında uzman konuşmacılar yapay zekanın günümüz ve gelecekteki etkilerini ele alacak. Makine öğrenimi ve yapay zeka ile ilgilenen tüm öğrencilerimizi bekliyoruz.'
        },
        '2': {
            title: 'Blockchain Teknolojileri Workshop',
            community: 'Yazılım ve Bilişim Topluluğu',
            communityImg: 'assets/community-icon.png',
            date: '18 Mayıs 2023',
            location: 'Bilgisayar Mühendisliği Lab',
            time: '13:00 - 17:00',
            image: 'assets/event2.jpg',
            description: 'Blockchain teknolojilerini tanıtacağımız bu workshop etkinliğinde, temel kripto kavramlarından akıllı kontrat uygulamalarına kadar geniş bir yelpazede pratik bilgiler edineceksiniz. Katılımcılar kendi basit blockchain uygulamalarını geliştirme fırsatı bulacak.'
        },
        '3': {
            title: 'Bahar Şenliği Konseri',
            community: 'Müzik Topluluğu',
            communityImg: 'assets/community-icon.png',
            date: '20 Mayıs 2023',
            location: 'Merkez Kampüs Amfi',
            time: '18:00 - 22:00',
            image: 'assets/event3.jpg',
            description: 'Geleneksel bahar şenliğimizde birbirinden yetenekli üniversite grupları ve solistleri sahne alacak. Türkçe pop, rock ve caz müziklerinden oluşan repertuvarımızla sizleri müziğin ritmine bırakmaya davet ediyoruz.'
        },
        '4': {
            title: 'Kariyer Günleri',
            community: 'Kariyer Merkezi',
            communityImg: 'assets/community-icon.png',
            date: '22 Mayıs 2023',
            location: 'İletişim Fakültesi Salonu',
            time: '10:00 - 16:00',
            image: 'assets/event4.jpg',
            description: 'Ankara Üniversitesi Kariyer Merkezi olarak düzenlediğimiz Kariyer Günleri etkinliğinde, alanında öncü şirketler ve kurumlar öğrencilerimizle buluşacak. CV hazırlama atölyeleri, mülakat simülasyonları ve networking fırsatları sizleri bekliyor.'
        },
        '5': {
            title: 'Shakespeare Hamlet Gösterisi',
            community: 'Tiyatro Topluluğu',
            communityImg: 'assets/community-icon.png',
            date: '25 Mayıs 2023',
            location: 'İletişim Fakültesi Tiyatro Salonu',
            time: '19:30 - 21:30',
            image: 'assets/event5.jpg',
            description: 'William Shakespeare\'in ölümsüz eseri Hamlet, tiyatro topluluğumuz tarafından modern bir uyarlamayla sahnelenecek. Danimarka sarayındaki entrika ve ihaneti konu alan bu klasik oyunu kaçırmayın.'
        },
        '6': {
            title: 'Eymir Gölü Temizlik Etkinliği',
            community: 'Doğa ve Çevre Topluluğu',
            communityImg: 'assets/community-icon.png',
            date: '27 Mayıs 2023',
            location: 'Eymir Gölü Giriş Kapısı',
            time: '09:00 - 13:00',
            image: 'assets/event6.jpg',
            description: 'Doğa ve Çevre Topluluğu olarak Eymir Gölü\'nde geniş kapsamlı bir temizlik etkinliği düzenliyoruz. Çevre bilincini artırmak ve doğal alanlarımızı korumak için tüm gönüllüleri bekliyoruz. Eldiven ve çöp poşetleri tarafımızdan sağlanacaktır.'
        },
        '7': {
            title: 'Türk Mutfağı Atölyesi',
            community: 'Gastronomi Topluluğu',
            communityImg: 'assets/community-icon.png',
            date: '29 Mayıs 2023',
            location: 'Ziraat Fakültesi Mutfak Atölyesi',
            time: '15:00 - 18:00',
            image: 'assets/event7.jpg',
            description: 'Geleneksel Türk mutfağının eşsiz lezzetlerini öğreneceğimiz bu atölyede, Anadolu\'nun zengin mutfak kültürünü tanıyacak ve uygulamalı olarak klasik tarifleri pişireceğiz. Katılım için önceden kayıt yaptırmanız gerekmektedir.'
        }
    };
    
    // Modal içeriğini güncelle
    const event = eventData[eventId];
    if (event) {
        document.getElementById('modalTitle').textContent = event.title;
        document.getElementById('modalCommunity').textContent = event.community;
        document.getElementById('modalCommunityImg').src = event.communityImg;
        document.getElementById('modalDate').textContent = event.date;
        document.getElementById('modalLocation').textContent = event.location;
        document.getElementById('modalTime').textContent = event.time;
        document.getElementById('modalImage').src = event.image;
        document.getElementById('modalImage').onerror = function() { this.src = 'assets/default-event.jpg'; };
        document.getElementById('modalDescription').textContent = event.description;
        
        // Modalı göster
        modal.style.display = 'block';
    }
}
