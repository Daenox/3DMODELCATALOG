/**
 * CatalogStore - Client-side data store for GitHub Pages (with IndexedDB for 3D files & images)
 */

// IndexedDB Helper for storing large 3D model blobs and images
const DB_NAME = '3DModelCatalogDB';
const DB_VERSION = 1;
const STORE_FILES = 'model_files';

function openCatalogDB() {
    return new Promise((resolve) => {
        if (!window.indexedDB) {
            resolve(null);
            return;
        }
        const req = indexedDB.open(DB_NAME, DB_VERSION);
        req.onupgradeneeded = (e) => {
            const db = e.target.result;
            if (!db.objectStoreNames.contains(STORE_FILES)) {
                db.createObjectStore(STORE_FILES);
            }
        };
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => {
            console.warn('IndexedDB unavailable, falling back:', req.error);
            resolve(null);
        };
    });
}

async function dbSaveFile(key, blobOrFile) {
    try {
        const db = await openCatalogDB();
        if (!db) return false;
        return new Promise((resolve) => {
            const tx = db.transaction(STORE_FILES, 'readwrite');
            const store = tx.objectStore(STORE_FILES);
            store.put(blobOrFile, key);
            tx.oncomplete = () => resolve(true);
            tx.onerror = () => resolve(false);
        });
    } catch (e) {
        return false;
    }
}

async function dbGetFile(key) {
    try {
        const db = await openCatalogDB();
        if (!db) return null;
        return new Promise((resolve) => {
            const tx = db.transaction(STORE_FILES, 'readonly');
            const store = tx.objectStore(STORE_FILES);
            const req = store.get(key);
            req.onsuccess = () => resolve(req.result || null);
            req.onerror = () => resolve(null);
        });
    } catch (e) {
        return null;
    }
}

async function dbDeleteFile(key) {
    try {
        const db = await openCatalogDB();
        if (!db) return;
        const tx = db.transaction(STORE_FILES, 'readwrite');
        tx.objectStore(STORE_FILES).delete(key);
    } catch (e) {}
}

const blobUrlCache = new Map();

const CatalogStore = {
    CUSTOM_KEY: '3d_catalog_custom_models',
    VIEWS_KEY: '3d_catalog_views',
    DELETED_KEY: '3d_catalog_deleted_ids',

    // IndexedDB access
    saveFile: dbSaveFile,
    getFile: dbGetFile,
    deleteFile: dbDeleteFile,

    async resolveModelBlobUrl(model) {
        if (!model) return model;
        if (model.model_file_key) {
            if (!blobUrlCache.has(model.model_file_key)) {
                const blob = await dbGetFile(model.model_file_key);
                if (blob) {
                    blobUrlCache.set(model.model_file_key, URL.createObjectURL(blob));
                }
            }
            if (blobUrlCache.has(model.model_file_key)) {
                model.model_file = blobUrlCache.get(model.model_file_key);
            }
        }
        return model;
    },

    getViews() {
        try {
            return JSON.parse(localStorage.getItem(this.VIEWS_KEY) || '{}');
        } catch (e) {
            return {};
        }
    },

    saveViews(views) {
        try {
            localStorage.setItem(this.VIEWS_KEY, JSON.stringify(views));
        } catch (e) {}
    },

    incrementViews(id) {
        const views = this.getViews();
        views[id] = (views[id] || 0) + 1;
        this.saveViews(views);
        return views[id];
    },

    getDeletedIds() {
        try {
            return JSON.parse(localStorage.getItem(this.DELETED_KEY) || '[]');
        } catch (e) {
            return [];
        }
    },

    getCustomModels() {
        try {
            return JSON.parse(localStorage.getItem(this.CUSTOM_KEY) || '[]');
        } catch (e) {
            return [];
        }
    },

    saveCustomModels(models) {
        try {
            localStorage.setItem(this.CUSTOM_KEY, JSON.stringify(models));
        } catch (e) {
            console.warn('localStorage save warning (quota):', e);
        }
    },

    getRawList() {
        const defaults = (window.DEFAULT_MODELS || []).map(m => ({ ...m }));
        const custom = this.getCustomModels();
        const deleted = new Set(this.getDeletedIds().map(String));
        const viewsMap = this.getViews();

        const combined = [...custom, ...defaults].filter(m => !deleted.has(String(m.id)));

        return combined.map(m => {
            const extraViews = viewsMap[String(m.id)] || 0;
            const modelObj = {
                ...m,
                views: (m.views || 0) + extraViews,
                photo_count: (m.photos && m.photos.length) ? m.photos.length : (m.photo_count || 0)
            };
            if (m.model_file_key && blobUrlCache.has(m.model_file_key)) {
                modelObj.model_file = blobUrlCache.get(m.model_file_key);
            }
            return modelObj;
        });
    },

    getAllModels({ query = '', category = '', tag = '', sort = 'newest' } = {}) {
        let list = this.getRawList();

        if (query) {
            const q = query.trim().toLowerCase();
            list = list.filter(m => 
                (m.title && m.title.toLowerCase().includes(q)) ||
                (m.description && m.description.toLowerCase().includes(q)) ||
                (m.tags && m.tags.toLowerCase().includes(q)) ||
                (m.category && m.category.toLowerCase().includes(q)) ||
                (m.author && m.author.toLowerCase().includes(q))
            );
        }

        if (tag) {
            const t = tag.trim().toLowerCase();
            list = list.filter(m => m.tags && m.tags.toLowerCase().includes(t));
        }

        if (category && category !== 'Всі') {
            list = list.filter(m => m.category === category);
        }

        if (sort === 'oldest') {
            list.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
        } else if (sort === 'views') {
            list.sort((a, b) => (b.views || 0) - (a.views || 0));
        } else if (sort === 'title') {
            list.sort((a, b) => (a.title || '').localeCompare(b.title || '', 'uk'));
        } else {
            // 'newest'
            list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        }

        return list;
    },

    getRecentModels(limit = 6) {
        const list = this.getAllModels({ sort: 'newest' });
        return list.slice(0, limit);
    },

    getModelById(id) {
        const list = this.getRawList();
        return list.find(m => String(m.id) === String(id)) || null;
    },

    getAllCategories() {
        const list = this.getRawList();
        const set = new Set();
        list.forEach(m => {
            if (m.category) set.add(m.category);
        });
        return ['Всі', ...Array.from(set)];
    },

    getPopularTags(limit = 10) {
        const list = this.getRawList();
        const counts = {};
        list.forEach(m => {
            if (m.tags) {
                m.tags.split(',').forEach(rawTag => {
                    const t = rawTag.trim();
                    if (t) {
                        counts[t] = (counts[t] || 0) + 1;
                    }
                });
            }
        });

        const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
        return sorted.slice(0, limit);
    },

    getStats() {
        const list = this.getRawList();
        const totalModels = list.length;
        const totalPhotos = list.reduce((sum, m) => sum + (m.photo_count || 0), 0);
        const totalViews = list.reduce((sum, m) => sum + (m.views || 0), 0);

        return {
            totalModels,
            totalPhotos,
            totalViews
        };
    },

    async addModel(data) {
        const custom = this.getCustomModels();
        const newId = Date.now();

        let modelFileKey = null;
        let modelFileUrl = data.model_file || '';

        // If user uploaded a 3D File (Blob/File)
        if (data.model_file_blob) {
            modelFileKey = `model_file_${newId}`;
            await dbSaveFile(modelFileKey, data.model_file_blob);
            blobUrlCache.set(modelFileKey, URL.createObjectURL(data.model_file_blob));
            modelFileUrl = blobUrlCache.get(modelFileKey);
        }

        const newModel = {
            id: newId,
            title: data.title,
            description: data.description || '',
            category: data.category || 'Загальне',
            tags: data.tags || '',
            thumbnail: data.thumbnail || '',
            model_file: modelFileUrl,
            model_file_key: modelFileKey,
            model_file_name: data.model_file_name || '',
            file_format: data.file_format || 'GLB',
            file_size: data.file_size || 0,
            poly_count: data.poly_count || '0',
            author: data.author || '3D Автор',
            views: 0,
            created_at: new Date().toISOString().replace('T', ' ').slice(0, 19),
            updated_at: new Date().toISOString().replace('T', ' ').slice(0, 19),
            photos: data.photos || []
        };
        newModel.photo_count = newModel.photos.length;

        custom.unshift(newModel);
        this.saveCustomModels(custom);
        return newId;
    },

    deleteModel(id) {
        const strId = String(id);
        const custom = this.getCustomModels();
        const target = custom.find(m => String(m.id) === strId);
        if (target && target.model_file_key) {
            dbDeleteFile(target.model_file_key);
            blobUrlCache.delete(target.model_file_key);
        }

        const filtered = custom.filter(m => String(m.id) !== strId);
        this.saveCustomModels(filtered);

        const deleted = this.getDeletedIds();
        if (!deleted.includes(strId)) {
            deleted.push(strId);
            try {
                localStorage.setItem(this.DELETED_KEY, JSON.stringify(deleted));
            } catch (e) {}
        }
        return true;
    },

    formatFilesize(bytes) {
        if (!bytes) return 'Невідомо';
        const num = parseFloat(bytes);
        if (isNaN(num)) return '0 Б';
        const units = ['Б', 'КБ', 'МБ', 'ГБ'];
        let size = num;
        for (let unit of units) {
            if (size < 1024.0) {
                return `${size.toFixed(1)} ${unit}`;
            }
            size /= 1024.0;
        }
        return `${size.toFixed(1)} ТБ`;
    },

    formatDate(dateStr) {
        if (!dateStr) return '';
        try {
            const d = new Date(dateStr.replace(' ', 'T'));
            if (isNaN(d.getTime())) return dateStr;
            const day = String(d.getDate()).padStart(2, '0');
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const year = d.getFullYear();
            return `${day}.${month}.${year}`;
        } catch (e) {
            return dateStr;
        }
    }
};

window.CatalogStore = CatalogStore;
