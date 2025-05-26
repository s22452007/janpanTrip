from django.core.management.base import BaseCommand
from travel.models import Region, AttractionType, Attraction
from decimal import Decimal

class Command(BaseCommand):
    help = '初始化基本的景點資料'

    def handle(self, *args, **options):
        self.stdout.write('開始初始化資料...')
        
        # 創建地區
        regions_data = [
            {'name': '東京', 'name_en': 'Tokyo', 'description': '日本的首都，現代化大都市'},
            {'name': '大阪', 'name_en': 'Osaka', 'description': '關西地區的經濟中心'},
            {'name': '京都', 'name_en': 'Kyoto', 'description': '古都，擁有豐富的歷史文化'},
            {'name': '沖繩', 'name_en': 'Okinawa', 'description': '南國島嶼，美麗的海灘'},
        ]
        
        for region_data in regions_data:
            region, created = Region.objects.get_or_create(
                name=region_data['name'],
                defaults=region_data
            )
            if created:
                self.stdout.write(f'創建地區: {region.name}')
        
        # 創建景點類型
        types_data = [
            {'name': '寺廟神社', 'icon': '⛩️'},
            {'name': '現代景點', 'icon': '🏢'},
            {'name': '自然風光', 'icon': '🌸'},
            {'name': '美食', 'icon': '🍣'},
            {'name': '購物娛樂', 'icon': '🛍️'},
        ]
        
        for type_data in types_data:
            attraction_type, created = AttractionType.objects.get_or_create(
                name=type_data['name'],
                defaults=type_data
            )
            if created:
                self.stdout.write(f'創建景點類型: {attraction_type.name}')
        
        # 創建景點
        tokyo = Region.objects.get(name='東京')
        modern = AttractionType.objects.get(name='現代景點')
        temple = AttractionType.objects.get(name='寺廟神社')
        
        attractions_data = [
            {
                'name': '東京晴空塔',
                'name_en': 'Tokyo Skytree',
                'description': '東京的新地標，高634米的電視塔，提供絕佳的城市景觀。',
                'region': tokyo,
                'attraction_type': modern,
                'address': '東京都墨田區押上1-1-2',
                'rating': Decimal('4.5'),
                'website': 'https://www.tokyo-skytree.jp/',
                'opening_hours': '8:00-22:00',
                'ticket_price': '成人2100日圓起',
            },
            {
                'name': '淺草寺',
                'name_en': 'Sensoji Temple',
                'description': '東京最古老的寺廟，建於645年，是東京最重要的文化景點之一。',
                'region': tokyo,
                'attraction_type': temple,
                'address': '東京都台東區淺草2-3-1',
                'rating': Decimal('4.4'),
                'opening_hours': '6:00-17:00',
                'ticket_price': '免費',
            },
            {
                'name': '明治神宮',
                'name_en': 'Meiji Shrine',
                'description': '供奉明治天皇和昭憲皇太后的神社，位於繁華的澀谷區中心。',
                'region': tokyo,
                'attraction_type': temple,
                'address': '東京都澀谷區代代木神園町1-1',
                'rating': Decimal('4.3'),
                'opening_hours': '5:00-18:00 (依季節調整)',
                'ticket_price': '免費',
            },
            {
                'name': '東京迪士尼樂園',
                'name_en': 'Tokyo Disneyland',
                'description': '亞洲第一座迪士尼主題樂園，充滿魔法與歡樂的世界。',
                'region': tokyo,
                'attraction_type': modern,
                'address': '千葉縣浦安市舞濱1-1',
                'rating': Decimal('4.6'),
                'website': 'https://www.tokyodisneyresort.jp/',
                'opening_hours': '8:00-22:00 (依季節調整)',
                'ticket_price': '成人8400日圓起',
            },
        ]
        
        for attraction_data in attractions_data:
            attraction, created = Attraction.objects.get_or_create(
                name=attraction_data['name'],
                defaults=attraction_data
            )
            if created:
                self.stdout.write(f'創建景點: {attraction.name}')
        
        self.stdout.write(
            self.style.SUCCESS('資料初始化完成！')
        )