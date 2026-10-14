import os
import urllib.request
import database
from PIL import Image, ImageDraw, ImageFont

def create_placeholder_image(filename, text, subtext, color1, color2):
    """Створює стильне градієнтне прев'ю-зображення з підписами"""
    width, height = 800, 600
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    # Плавний горизонтально-вертикальний градієнт
    for y in range(height):
        ratio_y = y / height
        for x in range(width):
            ratio_x = x / width
            blend = (ratio_x + ratio_y) / 2.0
            r = int(color1[0] * (1 - blend) + color2[0] * blend)
            g = int(color1[1] * (1 - blend) + color2[1] * blend)
            b = int(color1[2] * (1 - blend) + color2[2] * blend)
            img.putpixel((x, y), (r, g, b))
            
    # Додаємо сітку / техно-стиль
    draw = ImageDraw.Draw(img)
    for i in range(0, width, 40):
        draw.line([(i, 0), (i, height)], fill=(255, 255, 255, 20), width=1)
    for j in range(0, height, 40):
        draw.line([(0, j), (width, j)], fill=(255, 255, 255, 20), width=1)
        
    # Декоративна рамка
    draw.rectangle([20, 20, width - 20, height - 20], outline=(255, 255, 255, 80), width=2)
    draw.rectangle([25, 25, width - 25, height - 25], outline=(255, 255, 255, 40), width=1)
    
    # Текст
    draw.text((width // 2, height // 2 - 40), text, fill=(255, 255, 255), anchor="mm")
    draw.text((width // 2, height // 2 + 30), subtext, fill=(200, 230, 255), anchor="mm")
    draw.text((width // 2, height // 2 + 70), "3D MODEL VIEW / RENDER", fill=(160, 200, 255), anchor="mm")
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    img.save(filename, format="JPEG", quality=90)

def download_model(url, target_path):
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    if not os.path.exists(target_path):
        try:
            print(f"Завантаження {target_path}...")
            urllib.request.urlretrieve(url, target_path)
        except Exception as e:
            print(f"Помилка завантаження {url}: {e}")

def seed():
    database.init_db()
    
    # Перевіримо, чи база порожня
    recent = database.get_recent_models(1)
    if recent:
        print("База даних вже містить моделі. Пропускаємо початкове заповнення.")
        return

    print("Заповнення бази даних початковими моделями...")

    sample_models = [
        {
            "title": "Кіберпанк Бойовий Шолом",
            "description": "Деталізований шолом бойового дрона або пілота майбутнього з текстурами високої роздільної здатності PBR, слідами пошкоджень та потертостями скла.",
            "category": "Персонажі та Екіпірування",
            "tags": "sci-fi, кіберпанк, шолом, броня, зброя, high-poly",
            "poly_count": "45,200",
            "author": "TechVanguard Studio",
            "model_url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/DamagedHelmet/glTF-Binary/DamagedHelmet.glb",
            "model_file": "static/uploads/models/damaged_helmet.glb",
            "thumb_colors": ((30, 20, 60), (90, 30, 120)),
            "gallery": [
                {"sub": "Вид спереду (Front View)", "c1": (25, 20, 50), "c2": (120, 40, 160)},
                {"sub": "Деталізація візора (Wireframe & Texture)", "c1": (15, 35, 70), "c2": (40, 120, 180)},
                {"sub": "Рендер у студійному освітленні", "c1": (30, 40, 55), "c2": (80, 100, 130)},
            ]
        },
        {
            "title": "Ретро Фотоапарат Vintage 1950",
            "description": "Класична плівкова фотокамера середини XX століття. Металевий корпус, шкіряні вставки та скляна оптика. Ідеально для історичних ігор та візуалізацій.",
            "category": "Предмети та Реквізит",
            "tags": "ретро, фотокамера, вінтаж, техніка, реквізит, realistic",
            "poly_count": "24,800",
            "author": "ClassicProps",
            "model_url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/AntiqueCamera/glTF-Binary/AntiqueCamera.glb",
            "model_file": "static/uploads/models/antique_camera.glb",
            "thumb_colors": ((40, 35, 30), (130, 95, 60)),
            "gallery": [
                {"sub": "Макро об'єктива та затвора", "c1": (45, 40, 30), "c2": (160, 120, 80)},
                {"sub": "Задня панель та відкритий відсік плівки", "c1": (35, 30, 25), "c2": (110, 85, 60)},
                {"sub": "Ортографічна проекція збоку", "c1": (30, 30, 40), "c2": (90, 95, 110)},
            ]
        },
        {
            "title": "Кажанчик Резинова Качечка (Duck)",
            "description": "Легендарна жовта качка для ванної та дебагінгу коду. Еталонна 3D модель glTF стандарту Khronos Group з гладкими нормалями.",
            "category": "Іграшки та Сувеніри",
            "tags": "качка, іграшка, low-poly, жовтий, дебаг, мультяшний",
            "poly_count": "4,120",
            "author": "Sony Computer Entertainment",
            "model_url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Duck/glTF-Binary/Duck.glb",
            "model_file": "static/uploads/models/duck.glb",
            "thumb_colors": ((180, 120, 10), (240, 190, 40)),
            "gallery": [
                {"sub": "Рендер на воді з відблисками", "c1": (20, 80, 140), "c2": (220, 180, 30)},
                {"sub": "Сітка полігонів (Wireframe Mode)", "c1": (30, 30, 35), "c2": (230, 170, 20)},
            ]
        },
        {
            "title": "Вінтажний Бумбокс 80-х (BoomBox)",
            "description": "Справжній магнітофон епохи диско та брейкдансу. Подвійна касетна дека, радіоантена, динаміки високого діапазону та аналогові регулятори.",
            "category": "Електроніка та Аудіо",
            "tags": "бумбокс, музика, ретро, 80s, аудіо, стерео",
            "poly_count": "18,600",
            "author": "WaveAudio 3D",
            "model_url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/BoomBox/glTF-Binary/BoomBox.glb",
            "model_file": "static/uploads/models/boombox.glb",
            "thumb_colors": ((20, 30, 50), (40, 80, 120)),
            "gallery": [
                {"sub": "Панель управління та касетний привід", "c1": (25, 30, 45), "c2": (50, 95, 140)},
                {"sub": "Рендер у неоновому клубі", "c1": (50, 15, 60), "c2": (130, 30, 150)},
                {"sub": "Вигляд ззаду: порти підключення", "c1": (20, 25, 30), "c2": (70, 75, 85)},
            ]
        },
        {
            "title": "Старовинний Масляний Ліхтар",
            "description": "Атмосферний підвісний ліхтар для середньовічних та фентезійних сцен. Скляна колба, коване залізо та текстура патини.",
            "category": "Архітектура та Інтер'єр",
            "tags": "ліхтар, фентезі, середньовіччя, світло, кований метал, патина",
            "poly_count": "15,340",
            "author": "MedievalCraft",
            "model_url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Lantern/glTF-Binary/Lantern.glb",
            "model_file": "static/uploads/models/lantern.glb",
            "thumb_colors": ((40, 25, 15), (140, 70, 20)),
            "gallery": [
                {"sub": "Ефект палаючого вогню всередині", "c1": (60, 20, 10), "c2": (200, 100, 20)},
                {"sub": "Детальне кріплення ланцюга", "c1": (35, 30, 30), "c2": (90, 85, 80)},
            ]
        },
        {
            "title": "Органічне Авокадо (Food 3D Scan)",
            "description": "Фотограмметричний 3D скан свіжого авокадо з кісточкою. Реалістична мікротекстура шкірки та м'якоті. Підходить для кулінарних візуалізацій.",
            "category": "Природа та Їжа",
            "tags": "авокадо, їжа, органічний, скан, фотограмметрія, природа",
            "poly_count": "8,200",
            "author": "NatureScan 3D",
            "model_url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Avocado/glTF-Binary/Avocado.glb",
            "model_file": "static/uploads/models/avocado.glb",
            "thumb_colors": ((25, 45, 20), (70, 130, 45)),
            "gallery": [
                {"sub": "Текстура кісточки зблизька", "c1": (45, 30, 15), "c2": (110, 75, 40)},
                {"sub": "Рельєф шорсткої шкірки", "c1": (20, 40, 20), "c2": (50, 95, 40)},
                {"sub": "Композиція у розрізі", "c1": (30, 50, 25), "c2": (120, 160, 60)},
            ]
        }
    ]

    for idx, item in enumerate(sample_models, start=1):
        # Завантажуємо 3D модель
        download_model(item["model_url"], item["model_file"])
        
        # Створюємо обкладинку
        thumb_path = f"static/uploads/thumbnails/thumb_{idx}.jpg"
        create_placeholder_image(
            thumb_path, 
            item["title"], 
            f"Категорія: {item['category']}", 
            item["thumb_colors"][0], 
            item["thumb_colors"][1]
        )
        
        file_size = os.path.getsize(item["model_file"]) if os.path.exists(item["model_file"]) else 1024000
        
        model_id = database.add_model(
            title=item["title"],
            description=item["description"],
            category=item["category"],
            tags=item["tags"],
            thumbnail=thumb_path.replace('\\', '/'),
            model_file=item["model_file"].replace('\\', '/'),
            file_format="GLB",
            file_size=file_size,
            poly_count=item["poly_count"],
            author=item["author"]
        )
        
        # Додаємо фотографії галереї для кожної моделі
        for p_idx, photo_data in enumerate(item["gallery"], start=1):
            photo_path = f"static/uploads/photos/photo_{model_id}_{p_idx}.jpg"
            create_placeholder_image(
                photo_path,
                f"{item['title']} - Фото #{p_idx}",
                photo_data["sub"],
                photo_data["c1"],
                photo_data["c2"]
            )
            database.add_model_photo(
                model_id=model_id,
                photo_path=photo_path.replace('\\', '/'),
                caption=photo_data["sub"]
            )
            
    print("Початкові моделі та галереї фото успішно створено!")

if __name__ == "__main__":
    seed()
