import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'models.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    # Підтримка коректного нечутливого до регістру пошуку для кирилиці (української мови)
    conn.create_function("lower", 1, lambda s: str(s).lower() if s is not None else "")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Створення таблиці моделей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT DEFAULT 'Загальне',
            tags TEXT,
            thumbnail TEXT,
            model_file TEXT,
            file_format TEXT,
            file_size INTEGER DEFAULT 0,
            poly_count TEXT,
            author TEXT DEFAULT 'Автор',
            views INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Створення таблиці фотографій галереї для кожної моделі
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER NOT NULL,
            photo_path TEXT NOT NULL,
            caption TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (model_id) REFERENCES models (id) ON DELETE CASCADE
        )
    ''')
    
    # Індекси для швидкого пошуку
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_models_created ON models(created_at DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_models_category ON models(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_photos_model ON model_photos(model_id)')
    
    conn.commit()
    conn.close()

def get_recent_models(limit=6):
    conn = get_db_connection()
    models = conn.execute('''
        SELECT m.*, 
               (SELECT COUNT(*) FROM model_photos WHERE model_id = m.id) AS photo_count
        FROM models m
        ORDER BY m.created_at DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return models

def get_all_models(search_query=None, tag=None, category=None, sort_by='newest'):
    conn = get_db_connection()
    
    query = '''
        SELECT m.*, 
               (SELECT COUNT(*) FROM model_photos WHERE model_id = m.id) AS photo_count
        FROM models m
        WHERE 1=1
    '''
    params = []
    
    if search_query:
        query += ''' AND (
            LOWER(m.title) LIKE ? OR 
            LOWER(m.description) LIKE ? OR 
            LOWER(m.tags) LIKE ? OR
            LOWER(m.category) LIKE ?
        )'''
        search_pattern = f"%{search_query.strip().lower()}%"
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
        
    if tag:
        query += ' AND LOWER(m.tags) LIKE ?'
        params.append(f"%{tag.strip().lower()}%")
        
    if category and category != 'Всі':
        query += ' AND m.category = ?'
        params.append(category.strip())
        
    if sort_by == 'oldest':
        query += ' ORDER BY m.created_at ASC'
    elif sort_by == 'views':
        query += ' ORDER BY m.views DESC, m.created_at DESC'
    elif sort_by == 'title':
        query += ' ORDER BY m.title ASC'
    else:  # 'newest'
        query += ' ORDER BY m.created_at DESC'
        
    models = conn.execute(query, params).fetchall()
    conn.close()
    return models

def get_model_by_id(model_id):
    conn = get_db_connection()
    model = conn.execute('SELECT * FROM models WHERE id = ?', (model_id,)).fetchone()
    conn.close()
    return model

def get_model_photos(model_id):
    conn = get_db_connection()
    photos = conn.execute('SELECT * FROM model_photos WHERE model_id = ? ORDER BY id ASC', (model_id,)).fetchall()
    conn.close()
    return photos

def add_model(title, description, category, tags, thumbnail, model_file, file_format, file_size, poly_count, author):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO models (
            title, description, category, tags, thumbnail, 
            model_file, file_format, file_size, poly_count, author
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, description, category, tags, thumbnail, model_file, file_format, file_size, poly_count, author))
    model_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return model_id

def add_model_photo(model_id, photo_path, caption=''):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO model_photos (model_id, photo_path, caption)
        VALUES (?, ?, ?)
    ''', (model_id, photo_path, caption))
    photo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return photo_id

def update_model(model_id, title, description, category, tags, poly_count, author, thumbnail=None, model_file=None, file_format=None, file_size=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        UPDATE models 
        SET title = ?, description = ?, category = ?, tags = ?, poly_count = ?, author = ?, updated_at = CURRENT_TIMESTAMP
    '''
    params = [title, description, category, tags, poly_count, author]
    
    if thumbnail:
        query += ', thumbnail = ?'
        params.append(thumbnail)
    if model_file:
        query += ', model_file = ?, file_format = ?, file_size = ?'
        params.extend([model_file, file_format, file_size])
        
    query += ' WHERE id = ?'
    params.append(model_id)
    
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def delete_model_photo(photo_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    photo = cursor.execute('SELECT photo_path FROM model_photos WHERE id = ?', (photo_id,)).fetchone()
    cursor.execute('DELETE FROM model_photos WHERE id = ?', (photo_id,))
    conn.commit()
    conn.close()
    return photo['photo_path'] if photo else None

def delete_model(model_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    model = cursor.execute('SELECT thumbnail, model_file FROM models WHERE id = ?', (model_id,)).fetchone()
    photos = cursor.execute('SELECT photo_path FROM model_photos WHERE model_id = ?', (model_id,)).fetchall()
    
    cursor.execute('DELETE FROM models WHERE id = ?', (model_id,))
    conn.commit()
    conn.close()
    
    return {
        'model': model,
        'photos': [p['photo_path'] for p in photos]
    }

def increment_views(model_id):
    conn = get_db_connection()
    conn.execute('UPDATE models SET views = views + 1 WHERE id = ?', (model_id,))
    conn.commit()
    conn.close()

def get_all_tags():
    conn = get_db_connection()
    rows = conn.execute('SELECT tags FROM models WHERE tags IS NOT NULL AND tags != ""').fetchall()
    conn.close()
    
    tag_counts = {}
    for row in rows:
        tags_raw = row['tags'].split(',')
        for t in tags_raw:
            cleaned = t.strip()
            if cleaned:
                tag_counts[cleaned] = tag_counts.get(cleaned, 0) + 1
                
    # Сортування за популярністю
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_tags

def get_stats():
    conn = get_db_connection()
    total_models = conn.execute('SELECT COUNT(*) FROM models').fetchone()[0]
    total_photos = conn.execute('SELECT COUNT(*) FROM model_photos').fetchone()[0]
    total_views = conn.execute('SELECT COALESCE(SUM(views), 0) FROM models').fetchone()[0]
    categories = conn.execute('SELECT category, COUNT(*) as count FROM models GROUP BY category ORDER BY count DESC').fetchall()
    conn.close()
    return {
        'total_models': total_models,
        'total_photos': total_photos,
        'total_views': total_views,
        'categories': categories
    }
