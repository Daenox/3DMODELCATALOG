import os
import uuid
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for, 
    flash, jsonify, send_from_directory, send_file, abort
)
from werkzeug.utils import secure_filename
import database

app = Flask(__name__)
app.secret_key = 'super_secret_3d_gallery_key_replace_in_prod'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
MODELS_FOLDER = os.path.join(UPLOAD_FOLDER, 'models')
THUMBS_FOLDER = os.path.join(UPLOAD_FOLDER, 'thumbnails')
PHOTOS_FOLDER = os.path.join(UPLOAD_FOLDER, 'photos')

for folder in [MODELS_FOLDER, THUMBS_FOLDER, PHOTOS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

ALLOWED_MODEL_EXTENSIONS = {'glb', 'gltf', 'obj', 'stl', 'fbx', 'blend', 'zip'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, destination_folder):
    """Зберігає файл з унікальним іменем для уникнення колізій та збереження розширення"""
    if not file or file.filename == '':
        return None
    original_name = secure_filename(file.filename)
    extension = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'bin'
    unique_name = f"{uuid.uuid4().hex[:12]}_{original_name}"
    filepath = os.path.join(destination_folder, unique_name)
    file.save(filepath)
    # Повертаємо відносний шлях для static
    rel_path = os.path.relpath(filepath, BASE_DIR).replace('\\', '/')
    return rel_path

@app.template_filter('filesize')
def format_filesize(size_in_bytes):
    if not size_in_bytes:
        return "Невідомо"
    try:
        size = float(size_in_bytes)
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} ТБ"
    except Exception:
        return "0 Б"

@app.template_filter('format_date')
def format_date(value):
    if not value:
        return ""
    try:
        # SQLite CURRENT_TIMESTAMP: YYYY-MM-DD HH:MM:SS
        dt = datetime.strptime(str(value).split('.')[0], '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%d.%m.%Y')
    except Exception:
        return str(value)

@app.context_processor
def inject_global_data():
    """Додає категорії та статистику в усі шаблони"""
    categories = [
        'Всі',
        'Персонажі та Екіпірування',
        'Предмети та Реквізит',
        'Іграшки та Сувеніри',
        'Електроніка та Аудіо',
        'Архітектура та Інтер\'єр',
        'Транспорт та Техніка',
        'Природа та Їжа',
        'Зброя та Мілітарі',
        'Інше'
    ]
    return {
        'all_categories': categories,
        'current_year': datetime.now().year
    }

# --- Головна сторінка ---
@app.route('/')
def index():
    recent_models = database.get_recent_models(limit=6)
    stats = database.get_stats()
    popular_tags = database.get_all_tags()[:12]
    return render_template(
        'index.html', 
        recent_models=recent_models, 
        stats=stats,
        popular_tags=popular_tags
    )

# --- Вкладка Галереї ---
@app.route('/gallery')
def gallery():
    search_query = request.args.get('q', '').strip()
    tag = request.args.get('tag', '').strip()
    category = request.args.get('category', '').strip()
    sort_by = request.args.get('sort', 'newest')
    
    models = database.get_all_models(
        search_query=search_query,
        tag=tag,
        category=category,
        sort_by=sort_by
    )
    popular_tags = database.get_all_tags()[:20]
    
    return render_template(
        'gallery.html',
        models=models,
        search_query=search_query,
        current_tag=tag,
        current_category=category,
        current_sort=sort_by,
        popular_tags=popular_tags,
        total_results=len(models)
    )

# --- Детальний перегляд моделі ---
@app.route('/model/<int:model_id>')
def model_detail(model_id):
    model = database.get_model_by_id(model_id)
    if not model:
        flash('Модель не знайдено', 'danger')
        return redirect(url_for('gallery'))
        
    database.increment_views(model_id)
    photos = database.get_model_photos(model_id)
    
    # Схожі моделі за категорією
    related_models = [
        m for m in database.get_all_models(category=model['category'], sort_by='newest') 
        if m['id'] != model_id
    ][:4]
    
    tags_list = [t.strip() for t in model['tags'].split(',') if t.strip()] if model['tags'] else []
    
    return render_template(
        'model_detail.html',
        model=model,
        photos=photos,
        tags_list=tags_list,
        related_models=related_models
    )

# --- Додавання нової моделі (з формою та фотографіями галереї) ---
@app.route('/add', methods=['GET', 'POST'])
def add_model():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'Інше').strip()
        tags = request.form.get('tags', '').strip()
        poly_count = request.form.get('poly_count', '').strip()
        author = request.form.get('author', 'Анонім').strip()
        
        if not title:
            flash('Будь ласка, вкажіть назву моделі!', 'danger')
            return redirect(request.url)
            
        # Обробка 3D файлу моделі
        model_file = request.files.get('model_file')
        model_file_path = None
        file_format = None
        file_size = 0
        
        if model_file and model_file.filename != '':
            if allowed_file(model_file.filename, ALLOWED_MODEL_EXTENSIONS):
                model_file_path = save_uploaded_file(model_file, MODELS_FOLDER)
                file_format = model_file.filename.rsplit('.', 1)[1].upper()
                full_path = os.path.join(BASE_DIR, model_file_path)
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
            else:
                flash(f'Непідтримуваний формат 3D файлу. Дозволені: {", ".join(ALLOWED_MODEL_EXTENSIONS)}', 'warning')

        # Обробка головної обкладинки
        thumb_file = request.files.get('thumbnail')
        thumb_path = None
        if thumb_file and thumb_file.filename != '':
            if allowed_file(thumb_file.filename, ALLOWED_IMAGE_EXTENSIONS):
                thumb_path = save_uploaded_file(thumb_file, THUMBS_FOLDER)
            else:
                flash('Непідтримуваний формат обкладинки (дозволені: png, jpg, jpeg, webp, gif).', 'warning')
        
        # Додавання моделі до бази даних
        model_id = database.add_model(
            title=title,
            description=description,
            category=category,
            tags=tags,
            thumbnail=thumb_path,
            model_file=model_file_path,
            file_format=file_format,
            file_size=file_size,
            poly_count=poly_count,
            author=author or 'Анонім'
        )
        
        # Обробка додаткових фотографій галереї (можливість додавання фотографій для галереї)
        gallery_photos = request.files.getlist('gallery_photos')
        added_photos_count = 0
        for photo in gallery_photos:
            if photo and photo.filename != '' and allowed_file(photo.filename, ALLOWED_IMAGE_EXTENSIONS):
                photo_path = save_uploaded_file(photo, PHOTOS_FOLDER)
                if photo_path:
                    # Якщо головної обкладинки не було, перше фото галереї може стати обкладинкою
                    if not thumb_path and added_photos_count == 0:
                        database.update_model(model_id, title, description, category, tags, poly_count, author, thumbnail=photo_path)
                    
                    database.add_model_photo(model_id, photo_path, caption=photo.filename)
                    added_photos_count += 1
                    
        flash(f'Модель «{title}» успішно додана до каталогу! Завантажено {added_photos_count} фото до галереї.', 'success')
        return redirect(url_for('model_detail', model_id=model_id))
        
    return render_template('add_model.html')

# --- Редагування моделі ---
@app.route('/model/<int:model_id>/edit', methods=['GET', 'POST'])
def edit_model(model_id):
    model = database.get_model_by_id(model_id)
    if not model:
        flash('Модель не знайдено', 'danger')
        return redirect(url_for('gallery'))
        
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'Інше').strip()
        tags = request.form.get('tags', '').strip()
        poly_count = request.form.get('poly_count', '').strip()
        author = request.form.get('author', 'Анонім').strip()
        
        # Нова обкладинка (якщо обрано)
        thumb_file = request.files.get('thumbnail')
        new_thumb_path = None
        if thumb_file and thumb_file.filename != '' and allowed_file(thumb_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            new_thumb_path = save_uploaded_file(thumb_file, THUMBS_FOLDER)
            
        # Новий 3D файл (якщо обрано)
        model_file = request.files.get('model_file')
        new_model_path = None
        new_format = None
        new_size = None
        if model_file and model_file.filename != '' and allowed_file(model_file.filename, ALLOWED_MODEL_EXTENSIONS):
            new_model_path = save_uploaded_file(model_file, MODELS_FOLDER)
            new_format = model_file.filename.rsplit('.', 1)[1].upper()
            full_path = os.path.join(BASE_DIR, new_model_path)
            new_size = os.path.getsize(full_path) if os.path.exists(full_path) else 0

        database.update_model(
            model_id=model_id,
            title=title,
            description=description,
            category=category,
            tags=tags,
            poly_count=poly_count,
            author=author,
            thumbnail=new_thumb_path,
            model_file=new_model_path,
            file_format=new_format,
            file_size=new_size
        )
        
        # Додаткові нові фото галереї
        new_photos = request.files.getlist('gallery_photos')
        for photo in new_photos:
            if photo and photo.filename != '' and allowed_file(photo.filename, ALLOWED_IMAGE_EXTENSIONS):
                photo_path = save_uploaded_file(photo, PHOTOS_FOLDER)
                if photo_path:
                    database.add_model_photo(model_id, photo_path, caption=photo.filename)
                    
        flash('Зміни успішно збережено!', 'success')
        return redirect(url_for('model_detail', model_id=model_id))
        
    photos = database.get_model_photos(model_id)
    return render_template('edit_model.html', model=model, photos=photos)

# --- Видалення окремого фото з галереї ---
@app.route('/photo/<int:photo_id>/delete', methods=['POST'])
def delete_photo(photo_id):
    deleted_path = database.delete_model_photo(photo_id)
    if deleted_path:
        full_path = os.path.join(BASE_DIR, deleted_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except Exception:
                pass
    return jsonify({'success': True})

# --- Видалення моделі ---
@app.route('/model/<int:model_id>/delete', methods=['POST'])
def delete_model(model_id):
    data = database.delete_model(model_id)
    # Видалення файлів з диску
    if data:
        if data['model']:
            for key in ['thumbnail', 'model_file']:
                path = data['model'][key]
                if path:
                    full_path = os.path.join(BASE_DIR, path)
                    if os.path.exists(full_path):
                        try:
                            os.remove(full_path)
                        except Exception:
                            pass
        for photo_path in data.get('photos', []):
            if photo_path:
                full_path = os.path.join(BASE_DIR, photo_path)
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except Exception:
                        pass
                        
    flash('Модель успішно видалено!', 'info')
    return redirect(url_for('gallery'))

# --- Завантаження файлу 3D моделі ---
@app.route('/download/model/<int:model_id>')
def download_model(model_id):
    model = database.get_model_by_id(model_id)
    if not model or not model['model_file']:
        abort(404)
    file_path = os.path.join(BASE_DIR, model['model_file'])
    if not os.path.exists(file_path):
        abort(404)
    ext = model['file_format'].lower() if model['file_format'] else 'glb'
    download_name = f"{secure_filename(model['title'])}.{ext}"
    return send_file(file_path, as_attachment=True, download_name=download_name)

# --- Живий пошук API ---
@app.route('/api/search')
def api_search():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify([])
    models = database.get_all_models(search_query=q)
    results = []
    for m in models[:8]:
        results.append({
            'id': m['id'],
            'title': m['title'],
            'category': m['category'],
            'tags': m['tags'],
            'thumbnail': url_for('static', filename=m['thumbnail'].replace('static/', '')) if m['thumbnail'] else None,
            'url': url_for('model_detail', model_id=m['id'])
        })
    return jsonify(results)

if __name__ == '__main__':
    database.init_db()
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    print(f"Сервер 3D Галереї запущено на http://{host}:{port}")
    app.run(debug=True, host=host, port=port)
