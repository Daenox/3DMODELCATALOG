# 🌐 Повний посібник із підключення власного домену до 3D Галереї

У цьому проєкті підготовлено все необхідне, щоб сайт працював як повноцінний автономний веб-ресурс під власним доменом.

---

## 📌 Варіант 1. Локальний власний домен на комп'ютері (Безкоштовно, за 10 секунд)

Ви можете відкривати сайт прямо за красивою адресою (наприклад, **`http://3dgallery.local`**), без цифр `127.0.0.1:5000`!

### Як це зробити:
1. Запустіть файл **`setup_local_domain.bat`** (від імені адміністратора).
   - Він автоматично додасть запис `127.0.0.1 3dgallery.local` у файл `hosts` вашої Windows.
2. Запустіть **`start_domain_site.bat`** (або `server.py`).
3. Відкрийте у будь-якому браузері:
   👉 **`http://3dgallery.local`**

*(За бажанням, ви можете замінити `3dgallery.local` на будь-яке інше ім'я, наприклад `my3d.com` або `models.test`)*.

---

## 📌 Варіант 2. Публічний інтернет-домен через Cloudflare Tunnel (Рекомендовано!)

Якщо у вас є власний домен (наприклад `my3dgallery.com`, `name.ua` тощо) і ви хочете відкрити сайт з цього комп'ютера всьому світу:

1. Зареєструйтесь на [Cloudflare](https://dash.cloudflare.com/) (безкоштовно).
2. Завантажте утиліту **`cloudflared`** для Windows.
3. Виконайте команду:
   ```cmd
   cloudflared tunnel --url http://localhost:5000
   ```
4. Cloudflare надасть вам безпечну публічну URL-адресу з **HTTPS**, або прив'яже ваш зареєстрований домен (`3d.yourdomain.com`).
   - ✅ Не потрібна статична IP-адреса
   - ✅ Не потрібно відкривати порти в роутері
   - ✅ Автоматичний безкоштовний зелений замочок (SSL/HTTPS)

---

## 📌 Варіант 3. Хмарний хостинг (Render.com / Railway)

Якщо ви не хочете тримати комп'ютер постійно увімкненим:

1. Завантажте папку проєкту на свій GitHub репозиторій.
2. Зайдіть на [Render.com](https://render.com/) або [Railway.app](https://railway.app/).
3. Створіть новий **Web Service** із вашого репозиторію:
   - **Build Command**: `pip install -r requirements.txt && python seed_data.py`
   - **Start Command**: `gunicorn app:app` (або `python server.py 5000`)
4. У вкладці **Settings -> Custom Domains** введіть свій домен (наприклад `gallery.yourdomain.com`).
5. У вашого реєстратора домену (CityHost, Namecheap тощо) додайте вказаний **CNAME** або **A-запис**.
6. Сайт автоматично отримає безкоштовний SSL та працюватиме 24/7!

---

## 📌 Варіант 4. Оренда VPS (Ubuntu Linux + Docker + Nginx)

Для максимальної потужності та контролю в проєкті вже створено готові конфігураційні файли:

* [`Dockerfile`](file:///c:/Users/Daenox/Desktop/3DMODELCATALOG/Dockerfile) — збірка контейнера Python 3.12 з усіма графічними бібліотеками
* [`docker-compose.yml`](file:///c:/Users/Daenox/Desktop/3DMODELCATALOG/docker-compose.yml) — автоматичний запуск веб-сервера з постійним сховищем для 3D моделей
* [`nginx.conf`](file:///c:/Users/Daenox/Desktop/3DMODELCATALOG/nginx.conf) — зворотний проксі-сервер з кешуванням 3D файлів, Gzip стисненням та підтримкою SSL Certbot

### Команда запуску на сервері:
```bash
docker-compose up -d --build
```
Для отримання безкоштовного SSL-сертифіката:
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```
