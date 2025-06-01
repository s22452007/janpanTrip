from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from travel.models import Region, AttractionType, Attraction, UserProfile, Trip, Itinerary, FavoriteAttraction
from decimal import Decimal
from datetime import datetime, date, time

class Command(BaseCommand):
    help = '初始化簡化的旅遊資料'

    def handle(self, *args, **options):
        self.stdout.write('開始初始化資料...')
        
        # 創建測試用戶
        self.create_test_users()
        
        # 創建地區資料
        self.create_regions()
        
        # 創建景點類型
        self.create_attraction_types()
        
        # 創建景點資料
        self.create_attractions()
        
        # 創建示範收藏
        self.create_sample_favorites()
        
        self.stdout.write(self.style.SUCCESS('資料初始化完成！'))
    
    def create_test_users(self):
        users_data = [
            {'username': 'demo_user', 'email': 'demo@example.com', 'password': 'demo123456', 'permission': 'user'},
            {'username': 'admin_user', 'email': 'admin@example.com', 'password': 'admin123456', 'permission': 'admin'},
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': '測試',
                    'last_name': '用戶'
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'email': user_data['email'],  # 添加這行
                        'phone': '0912345678',
                        'permission': user_data['permission']
                    }
                )
                self.stdout.write(f'創建用戶: {user.username} ({user_data["permission"]})')
    
    def create_regions(self):
        regions_data = [
        {'name': '東京'},
        {'name': '大阪'},
        {'name': '京都'},
        {'name': '奈良'},
        {'name': '沖繩'},
        {'name': '北海道'},
    ]
        
        for region_data in regions_data:
            region, created = Region.objects.get_or_create(
                name=region_data['name'],
                defaults=region_data
            )
            if created:
                self.stdout.write(f'創建地區: {region.name}')
    
    def create_attraction_types(self):
        types_data = [
            {'name': '寺廟神社', 'icon': '⛩️'},
            {'name': '現代景點', 'icon': '🏢'},
            {'name': '自然風光', 'icon': '🌸'},
            {'name': '美食', 'icon': '🍣'},
            {'name': '購物娛樂', 'icon': '🛍️'},
            {'name': '歷史古蹟', 'icon': '🏰'},
            {'name': '主題樂園', 'icon': '🎡'},
        ]
        
        for type_data in types_data:
            attraction_type, created = AttractionType.objects.get_or_create(
                name=type_data['name'],
                defaults=type_data
            )
            if created:
                self.stdout.write(f'創建景點類型: {attraction_type.name}')
    
    def create_attractions(self):
        # 獲取地區和類型
        tokyo = Region.objects.get(name='東京')
        osaka = Region.objects.get(name='大阪')
        kyoto = Region.objects.get(name='京都')
        
        temple = AttractionType.objects.get(name='寺廟神社')
        modern = AttractionType.objects.get(name='現代景點')
        food = AttractionType.objects.get(name='美食')
        theme_park = AttractionType.objects.get(name='主題樂園')
        historic = AttractionType.objects.get(name='歷史古蹟')
        
        attractions_data = [
            # 東京景點
            {
                'name': '東京晴空塔',
                'description': '東京的新地標，高634米的電視塔，提供絕佳的城市景觀。',
                'region': tokyo,
                'attraction_type': modern,
                'address': '東京都墨田區押上1-1-2',
                'website': 'https://www.tokyo-skytree.jp/',
                'phone': '0570-55-0634',
                'opening_hours': '8:00-22:00',
                'features': '360度全景觀景台、購物中心、水族館',
            },
            {
                'name': '淺草寺',
                'description': '東京最古老的寺廟，建於645年，雷門是著名的象徵。',
                'region': tokyo,
                'attraction_type': temple,
                'address': '東京都台東區淺草2-3-1',
                'opening_hours': '6:00-17:00',
                'features': '雷門、五重塔、仲見世通商店街',
            },
            {
                'name': '明治神宮',
                'description': '供奉明治天皇和昭憲皇太后的神社，位於原宿附近。',
                'region': tokyo,
                'attraction_type': temple,
                'address': '東京都澀谷區代代木神園町1-1',
                'opening_hours': '5:00-18:00',
                'features': '神宮御苑、寶物殿、大鳥居',
            },
            {
                'name': '東京迪士尼樂園',
                'description': '亞洲第一座迪士尼主題樂園，充滿魔法與歡樂。',
                'region': tokyo,
                'attraction_type': theme_park,
                'address': '千葉縣浦安市舞濱1-1',
                'website': 'https://www.tokyodisneyresort.jp/',
                'phone': '045-330-5211',
                'opening_hours': '8:00-22:00',
                'features': '七大主題園區、遊行表演、煙火秀',
            },
            {
                'name': '築地場外市場',
                'description': '東京著名的海鮮市場，品嚐最新鮮的壽司和海鮮。',
                'region': tokyo,
                'attraction_type': food,
                'address': '東京都中央區築地4-16-2',
                'opening_hours': '5:00-14:00',
                'features': '新鮮海鮮、壽司、玉子燒',
            },
            {
                'name': '澀谷十字路口',
                'description': '世界最繁忙的路口，東京的象徵性景點。',
                'region': tokyo,
                'attraction_type': modern,
                'address': '東京都澀谷區道玄坂2-1',
                'opening_hours': '24小時',
                'features': '忠犬八公像、澀谷天空觀景台、購物中心',
            },
            
            # 大阪景點
            {
                'name': '大阪城',
                'description': '豐臣秀吉建造的名城，大阪的象徵。',
                'region': osaka,
                'attraction_type': historic,
                'address': '大阪府大阪市中央區大阪城1-1',
                'phone': '06-6941-3044',
                'opening_hours': '9:00-17:00',
                'features': '天守閣、大阪城公園、櫻花季美景',
            },
            {
                'name': '道頓堀',
                'description': '大阪最熱鬧的商業區，美食和購物天堂。',
                'region': osaka,
                'attraction_type': food,
                'address': '大阪府大阪市中央區道頓堀',
                'opening_hours': '24小時',
                'features': '章魚燒、大阪燒、格力高跑跑人看板',
            },
            {
                'name': '環球影城',
                'description': '日本環球影城，哈利波特魔法世界等熱門設施。',
                'region': osaka,
                'attraction_type': theme_park,
                'address': '大阪府大阪市此花區櫻島2-1-33',
                'website': 'https://www.usj.co.jp/',
                'phone': '0570-20-0606',
                'opening_hours': '8:30-22:00',
                'features': '哈利波特園區、小小兵樂園、侏羅紀公園',
            },
            
            # 京都景點
            {
                'name': '清水寺',
                'description': '京都最著名的寺廟，以木造舞台和櫻花聞名。',
                'region': kyoto,
                'attraction_type': temple,
                'address': '京都府京都市東山區清水1-294',
                'phone': '075-551-1234',
                'opening_hours': '6:00-18:00',
                'features': '木造舞台、音羽瀑布、三年坂二年坂',
            },
            {
                'name': '伏見稻荷大社',
                'description': '以千本鳥居聞名的稻荷神社，京都必訪景點。',
                'region': kyoto,
                'attraction_type': temple,
                'address': '京都府京都市伏見區深草薮之內町68',
                'phone': '075-641-7331',
                'opening_hours': '24小時',
                'features': '千本鳥居、稻荷山登山步道',
            },
            {
                'name': '金閣寺',
                'description': '室町時代的金色舍利殿，京都最具代表性的寺廟。',
                'region': kyoto,
                'attraction_type': temple,
                'address': '京都府京都市北區金閣寺町1',
                'phone': '075-461-0013',
                'opening_hours': '9:00-17:00',
                'features': '金色舍利殿、鏡湖池、日式庭園',
            },
        ]
        
        for attraction_data in attractions_data:
            attraction, created = Attraction.objects.get_or_create(
                name=attraction_data['name'],
                defaults=attraction_data
            )
            if created:
                self.stdout.write(f'創建景點: {attraction.name}')
    
    def create_sample_favorites(self):
        # 創建一些示範收藏
        demo_user = User.objects.get(username='demo_user')
        attractions = Attraction.objects.all()[:5]  # 取前5個景點
        
        for attraction in attractions:
            favorite, created = FavoriteAttraction.objects.get_or_create(
                user=demo_user,
                attraction=attraction
            )
            if created:
                self.stdout.write(f'創建收藏: {demo_user.username} 收藏 {attraction.name}')