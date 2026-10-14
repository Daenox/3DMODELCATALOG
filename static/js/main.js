/**
 * 3D Model Catalog & Gallery - Interactive JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    initLightbox();
    initHeaderLiveSearch();
});

/* ==========================================================================
   Preview for Main Thumbnail
   ========================================================================== */
function previewThumbnail(input) {
    const container = document.getElementById('thumb-preview-container');
    const img = document.getElementById('thumb-preview-img');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            img.src = e.target.result;
            container.classList.remove('hidden');
        };
        reader.readAsDataURL(input.files[0]);
    } else {
        container.classList.add('hidden');
    }
}

/* ==========================================================================
   Preview for Multiple Gallery Photos (Додавання фотографій для галереї)
   ========================================================================== */
function previewGalleryPhotos(input) {
    const section = document.getElementById('gallery-previews-section');
    const grid = document.getElementById('gallery-previews-grid');
    const badge = document.getElementById('gallery-count-badge');
    
    if (!section || !grid) return;
    
    grid.innerHTML = '';
    
    if (input.files && input.files.length > 0) {
        const count = input.files.length;
        badge.innerHTML = `<i class="fa-solid fa-check-circle mr-1 text-emerald-400"></i> Обрано ${count} ${getPhotoPlural(count)} для галереї:`;
        section.classList.remove('hidden');
        
        Array.from(input.files).forEach((file, index) => {
            if (!file.type.startsWith('image/')) return;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                const card = document.createElement('div');
                card.className = 'relative aspect-[4/3] rounded-xl overflow-hidden bg-dark-950 border border-amber-500/40 shadow-sm animate-fadeIn';
                card.innerHTML = `
                    <img src="${e.target.result}" alt="${file.name}" class="w-full h-full object-cover">
                    <div class="absolute bottom-0 inset-x-0 bg-dark-950/80 px-1.5 py-1 text-[10px] text-slate-300 truncate font-mono">
                        ${file.name}
                    </div>
                    <span class="absolute top-1 left-1 bg-dark-900/80 text-amber-300 px-1.5 py-0.5 rounded text-[9px] font-bold">
                        #${index + 1}
                    </span>
                `;
                grid.appendChild(card);
            };
            reader.readAsDataURL(file);
        });
    } else {
        section.classList.add('hidden');
    }
}

function clearGalleryPhotos() {
    const input = document.getElementById('gallery_photos');
    if (input) input.value = '';
    const section = document.getElementById('gallery-previews-section');
    if (section) section.classList.add('hidden');
}

function getPhotoPlural(n) {
    if (n % 10 === 1 && n % 100 !== 11) return 'фотографію';
    if ([2, 3, 4].includes(n % 10) && ![12, 13, 14].includes(n % 100)) return 'фотографії';
    return 'фотографій';
}

/* ==========================================================================
   Fullscreen Lightbox for Gallery Photos
   ========================================================================== */
let currentLightboxIndex = 0;
let lightboxImages = [];

function initLightbox() {
    const lightbox = document.getElementById('photo-lightbox');
    const closeBtn = document.getElementById('lightbox-close');
    const prevBtn = document.getElementById('lightbox-prev');
    const nextBtn = document.getElementById('lightbox-next');
    
    if (!lightbox) return;

    // Collect all gallery items on model_detail page
    const items = document.querySelectorAll('.gallery-image-item');
    lightboxImages = Array.from(items).map(img => ({
        src: img.getAttribute('data-full') || img.src,
        caption: img.getAttribute('data-caption') || ''
    }));

    if (closeBtn) {
        closeBtn.addEventListener('click', closeLightbox);
    }
    if (prevBtn) {
        prevBtn.addEventListener('click', prevLightboxImage);
    }
    if (nextBtn) {
        nextBtn.addEventListener('click', nextLightboxImage);
    }

    // Close on click outside image
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) {
            closeLightbox();
        }
    });

    // Keyboard support
    document.addEventListener('keydown', (e) => {
        if (!lightbox.classList.contains('hidden')) {
            if (e.key === 'Escape') closeLightbox();
            if (e.key === 'ArrowLeft') prevLightboxImage();
            if (e.key === 'ArrowRight') nextLightboxImage();
        }
    });
}

function openLightbox(index) {
    const lightbox = document.getElementById('photo-lightbox');
    if (!lightbox || lightboxImages.length === 0) return;
    
    currentLightboxIndex = index;
    updateLightboxContent();
    lightbox.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeLightbox() {
    const lightbox = document.getElementById('photo-lightbox');
    if (!lightbox) return;
    lightbox.classList.add('hidden');
    document.body.style.overflow = '';
}

function prevLightboxImage() {
    if (lightboxImages.length === 0) return;
    currentLightboxIndex = (currentLightboxIndex - 1 + lightboxImages.length) % lightboxImages.length;
    updateLightboxContent();
}

function nextLightboxImage() {
    if (lightboxImages.length === 0) return;
    currentLightboxIndex = (currentLightboxIndex + 1) % lightboxImages.length;
    updateLightboxContent();
}

function updateLightboxContent() {
    const img = document.getElementById('lightbox-img');
    const caption = document.getElementById('lightbox-caption');
    const counter = document.getElementById('lightbox-counter');
    
    if (!lightboxImages[currentLightboxIndex]) return;
    
    const current = lightboxImages[currentLightboxIndex];
    img.src = current.src;
    caption.textContent = current.caption;
    counter.textContent = `${currentLightboxIndex + 1} з ${lightboxImages.length}`;
}

/* ==========================================================================
   Live Search in Header
   ========================================================================== */
function initHeaderLiveSearch() {
    const input = document.getElementById('header-search-input');
    const dropdown = document.getElementById('search-dropdown');
    const resultsList = document.getElementById('search-results-list');
    
    if (!input || !dropdown || !resultsList) return;
    
    let debounceTimer = null;
    
    input.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim();
        
        if (query.length < 2) {
            dropdown.classList.add('hidden');
            return;
        }
        
        debounceTimer = setTimeout(() => {
            fetch(`/api/search?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    resultsList.innerHTML = '';
                    if (data.length === 0) {
                        resultsList.innerHTML = `
                            <div class="p-4 text-xs text-slate-400 text-center">
                                Моделей за запитом «${query}» не знайдено
                            </div>
                        `;
                    } else {
                        data.forEach(item => {
                            const row = document.createElement('a');
                            row.href = item.url;
                            row.className = 'flex items-center gap-3 p-3 hover:bg-dark-800 transition-colors group';
                            
                            const thumbHtml = item.thumbnail 
                                ? `<img src="${item.thumbnail}" class="w-10 h-10 object-cover rounded-lg border border-dark-700">`
                                : `<div class="w-10 h-10 rounded-lg bg-dark-900 border border-dark-700 flex items-center justify-center text-slate-500"><i class="fa-solid fa-cube text-xs"></i></div>`;
                                
                            row.innerHTML = `
                                ${thumbHtml}
                                <div class="flex-1 min-w-0">
                                    <h4 class="text-xs font-bold text-slate-200 group-hover:text-brand-400 transition-colors truncate">${item.title}</h4>
                                    <div class="flex items-center gap-2 text-[10px] text-slate-400 mt-0.5">
                                        <span>${item.category}</span>
                                        ${item.tags ? `<span>• ${item.tags.split(',')[0]}</span>` : ''}
                                    </div>
                                </div>
                                <i class="fa-solid fa-chevron-right text-[10px] text-slate-600 group-hover:text-slate-400 group-hover:translate-x-0.5 transition-all"></i>
                            `;
                            resultsList.appendChild(row);
                        });
                        
                        // "Переглянути всі в галереї" посилання
                        const footerLink = document.createElement('a');
                        footerLink.href = `/gallery?q=${encodeURIComponent(query)}`;
                        footerLink.className = 'block p-2.5 bg-dark-900 hover:bg-dark-750 text-center text-xs font-semibold text-brand-400 border-t border-dark-700/60 transition-colors';
                        footerLink.innerHTML = `Переглянути всі результати в Галереї &rarr;`;
                        resultsList.appendChild(footerLink);
                    }
                    dropdown.classList.remove('hidden');
                })
                .catch(err => {
                    console.error('Error fetching search results:', err);
                });
        }, 220);
    });
    
    // Close dropdown on click outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('#header-search-container')) {
            dropdown.classList.add('hidden');
        }
    });
}
