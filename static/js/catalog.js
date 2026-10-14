/**
 * CatalogStore - Client-side data store for GitHub Pages
 */
const CatalogStore = {
    CUSTOM_KEY: '3d_catalog_custom_models',
    VIEWS_KEY: '3d_catalog_views',
    DELETED_KEY: '3d_catalog_deleted_ids',

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
        } catch (e) {}
    },

    getRawList() {
        const defaults = (window.DEFAULT_MODELS || []).map(m => ({ ...m }));
        const custom = this.getCustomModels();
        const deleted = new Set(this.getDeletedIds().map(String));
        const viewsMap = this.getViews();

        const combined = [...custom, ...defaults].filter(m => !deleted.has(String(m.id)));

        return combined.map(m => {
            const extraViews = viewsMap[String(m.id)] || 0;
            return {
                ...m,
                views: (m.views || 0) + extraViews,
                photo_count: (m.photos && m.photos.length) ? m.photos.length : (m.photo_count || 0)
            };
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

    addModel(data) {
        const custom = this.getCustomModels();
        const newModel = {
            id: Date.now(),
            title: data.title,
            description: data.description || '',
            category: data.category || 'Загальне',
            tags: data.tags || '',
            thumbnail: data.thumbnail || '',
            model_file: data.model_file || '',
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
        return newModel.id;
    },

    deleteModel(id) {
        const strId = String(id);
        const custom = this.getCustomModels().filter(m => String(m.id) !== strId);
        this.saveCustomModels(custom);

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
