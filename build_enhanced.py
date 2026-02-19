#!/usr/bin/env python3
"""Build enhanced alnafl_media_review.html from template + POI data."""
import re

with open('alnafl_media_review.html', 'r', encoding='utf-8') as f:
    orig = f.read()

with open('_poi_extract.txt', 'r', encoding='utf-8') as f:
    poi_html = f.read()

# Build enhanced template (user's design)
template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Al Nafl | Media Discovery Hub</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --brand-primary: #6366f1;
            --brand-secondary: #4f46e5;
            --bg-page: #0f172a;
            --bg-card: #1e293b;
            --bg-sidebar: #111827;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #334155;
            --sidebar-width: 280px;
        }

        * { box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            margin: 0;
            background: var(--bg-page);
            color: var(--text-main);
            overflow: hidden;
            display: flex;
            height: 100vh;
        }

        #gate {
            position: fixed;
            inset: 0;
            z-index: 10000;
            background: radial-gradient(circle at center, #1e293b, #020617);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .gate-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(20px);
            padding: 3rem;
            border-radius: 2rem;
            width: 100%;
            max-width: 420px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        }
        .gate-card h1 { font-size: 1.5rem; margin-bottom: 0.5rem; }
        .gate-card p { color: var(--text-muted); margin-bottom: 2rem; }
        .gate-card input {
            width: 100%;
            padding: 1rem;
            border-radius: 0.75rem;
            border: 1px solid var(--border-color);
            background: #0f172a;
            color: white;
            font-size: 1rem;
            text-align: center;
            margin-bottom: 1rem;
        }
        .gate-card button {
            width: 100%;
            padding: 1rem;
            background: var(--brand-primary);
            color: white;
            border: none;
            border-radius: 0.75rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
        }
        #gate.hidden { display: none; }

        aside {
            width: var(--sidebar-width);
            background: var(--bg-sidebar);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            padding: 1.5rem;
            flex-shrink: 0;
        }
        .sidebar-header h2 { font-size: 1.25rem; margin: 0; font-weight: 700; color: var(--brand-primary); }
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem;
            margin: 1.5rem 0;
        }
        .stat-box {
            background: var(--bg-card);
            padding: 0.75rem;
            border-radius: 0.75rem;
            text-align: center;
            border: 1px solid var(--border-color);
        }
        .stat-box small { display: block; color: var(--text-muted); font-size: 0.7rem; margin-bottom: 2px; }
        .stat-box span { font-weight: 700; font-size: 1.1rem; }

        .search-container input {
            width: 100%;
            background: #0f172a;
            border: 1px solid var(--border-color);
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
            color: white;
            font-family: inherit;
        }

        .filter-section { margin-top: 1.5rem; }
        .filter-label { font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.05em; margin-bottom: 0.5rem; display: block; }
        .filter-group { display: flex; flex-direction: column; gap: 0.5rem; }
        .filter-btn {
            background: transparent;
            color: var(--text-muted);
            border: 1px solid transparent;
            padding: 0.6rem 1rem;
            border-radius: 0.5rem;
            text-align: left;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 500;
        }
        .filter-btn:hover { background: rgba(255,255,255,0.05); color: white; }
        .filter-btn.active { background: var(--brand-primary); color: white; }

        main {
            flex-grow: 1;
            overflow-y: auto;
            padding: 2rem;
            scroll-behavior: smooth;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
        }

        .poi-card {
            background: var(--bg-card);
            border-radius: 1rem;
            overflow: hidden;
            border: 1px solid var(--border-color);
            transition: transform 0.2s, border-color 0.2s;
            display: flex;
            flex-direction: column;
        }
        .poi-card:hover { transform: translateY(-4px); border-color: var(--brand-primary); }

        .poi-gallery {
            position: relative;
            height: 180px;
            background: #0f172a;
            overflow: hidden;
            border-radius: 0.5rem 0.5rem 0 0;
        }
        .carousel-track {
            display: flex;
            overflow-x: auto;
            overflow-y: hidden;
            height: 100%;
            scroll-snap-type: x mandatory;
            scroll-behavior: smooth;
            -webkit-overflow-scrolling: touch;
        }
        .carousel-track::-webkit-scrollbar { height: 4px; }
        .carousel-track::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 2px; }
        .gallery-item {
            flex: 0 0 100%;
            width: 100%;
            min-width: 100%;
            position: relative;
            cursor: pointer;
            overflow: hidden;
            background: #111827;
            scroll-snap-align: start;
        }
        .gallery-item img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
        .gallery-item:hover img { transform: scale(1.05); }
        .gallery-item.video { background: #1e293b; }
        .gallery-item.video::after { content: "▶"; position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: rgba(255,255,255,0.6); font-size: 2.5rem; }
        .carousel-nav {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(0,0,0,0.5);
            border: none;
            color: white;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2;
            transition: background 0.2s;
        }
        .carousel-nav:hover { background: rgba(99, 102, 241, 0.8); }
        .carousel-prev { left: 0.5rem; }
        .carousel-next { right: 0.5rem; }
        .carousel-nav.hidden { display: none; }
        .media-count {
            position: absolute;
            bottom: 0.5rem;
            right: 0.5rem;
            background: rgba(0,0,0,0.7);
            color: var(--text-muted);
            font-size: 0.7rem;
            padding: 0.25rem 0.6rem;
            border-radius: 1rem;
            z-index: 2;
        }
        .carousel-indicator {
            position: absolute;
            bottom: 0.5rem;
            left: 0.5rem;
            color: var(--text-muted);
            font-size: 0.7rem;
            z-index: 2;
        }

        .poi-info { padding: 1.25rem; flex-grow: 1; }
        .poi-info h3 { margin: 0; font-size: 1.1rem; font-weight: 600; line-height: 1.4; }
        .poi-tags { margin-top: 0.75rem; display: flex; flex-wrap: wrap; gap: 0.5rem; }
        .chip { font-size: 0.7rem; padding: 0.2rem 0.6rem; border-radius: 2rem; background: rgba(99, 102, 241, 0.1); color: var(--brand-primary); border: 1px solid rgba(99, 102, 241, 0.2); }
        .chip.category { background: rgba(148, 163, 184, 0.1); color: var(--text-muted); border: none; }

        .poi-footer {
            padding: 0.75rem 1.25rem;
            background: rgba(0,0,0,0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .maps-link { color: var(--brand-primary); text-decoration: none; font-size: 0.8rem; font-weight: 600; }
        .maps-link:hover { text-decoration: underline; }

        #lightbox {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(2, 6, 23, 0.98);
            z-index: 20000;
            flex-direction: column;
        }
        #lightbox.show { display: flex; }
        .lb-header { padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.5); }
        .lb-main { flex-grow: 1; display: flex; align-items: center; justify-content: center; position: relative; padding: 2rem; }
        .lb-content { max-width: 90vw; max-height: 80vh; border-radius: 0.5rem; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); }
        .lb-nav {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255,255,255,0.05);
            border: none;
            color: white;
            padding: 2rem 1rem;
            cursor: pointer;
            border-radius: 0.5rem;
            font-size: 2rem;
        }
        .lb-nav:hover { background: rgba(255,255,255,0.1); }
        .lb-prev { left: 1rem; }
        .lb-next { right: 1rem; }
        .lb-close { background: none; border: none; color: white; font-size: 2rem; cursor: pointer; }

        .lb-footer { padding: 1.5rem; background: rgba(0,0,0,0.5); text-align: center; }
        .tag-manager { display: flex; justify-content: center; gap: 0.5rem; flex-wrap: wrap; }
        .tag-btn { background: #334155; border: none; color: white; padding: 0.4rem 1rem; border-radius: 2rem; cursor: pointer; font-size: 0.8rem; }
        .tag-btn.active { background: var(--brand-primary); }

        @media (max-width: 1024px) {
            body { flex-direction: column; }
            aside { width: 100%; height: auto; border-left: none; border-bottom: 1px solid var(--border-color); }
            main { height: auto; overflow: visible; }
        }
    </style>
</head>
<body>

    <div id="gate">
        <div class="gate-card">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🛰️</div>
            <h1>Al Nafl Discovery</h1>
            <p>Enter password to access media database</p>
            <input type="password" id="gate-password" placeholder="Password">
            <button onclick="checkGate()">Login</button>
            <div id="gate-error" style="color: #ef4444; margin-top: 1rem; display: none;">Invalid password</div>
        </div>
    </div>

    <aside>
        <div class="sidebar-header">
            <h2>Al Nafl Media</h2>
        </div>

        <div class="stats-grid">
            <div class="stat-box">
                <small>Total Sites</small>
                <span id="stat-pois">412</span>
            </div>
            <div class="stat-box">
                <small>Media</small>
                <span id="stat-media">798</span>
            </div>
        </div>

        <div class="search-container">
            <input type="text" id="search-input" placeholder="Search site or category..." oninput="handleSearch()">
        </div>

        <div class="filter-section">
            <span class="filter-label">Show Sites</span>
            <div class="filter-group">
                <button class="filter-btn active" data-filter="all" onclick="setFilter('all')">All</button>
                <button class="filter-btn" data-filter="media" onclick="setFilter('media')">With media only</button>
                <button class="filter-btn" data-filter="no-media" onclick="setFilter('no-media')">No media</button>
            </div>
        </div>

        <div class="filter-section">
            <span class="filter-label">By Tag</span>
            <div class="filter-group" id="tag-filters">
                <button class="filter-btn" data-tag="" onclick="setTagFilter('')">All tags</button>
            </div>
        </div>

        <div style="margin-top: auto; padding-top: 1rem;">
            <button onclick="logout()" style="width: 100%; background: none; border: 1px solid var(--border-color); color: var(--text-muted); padding: 0.5rem; border-radius: 0.5rem; cursor: pointer;">Logout</button>
        </div>
    </aside>

    <main id="scroll-container">
        <div class="grid" id="poi-grid"></div>
    </main>

    <div id="lightbox">
        <div class="lb-header">
            <h3 id="lb-title" style="margin:0; font-size: 1rem;">POI Title</h3>
            <button class="lb-close" onclick="closeLightbox()">&times;</button>
        </div>
        <div class="lb-main">
            <button class="lb-nav lb-next" onclick="navigateMedia(1)">❮</button>
            <img id="lb-img" class="lb-content" src="">
            <video id="lb-video" class="lb-content" controls style="display:none"></video>
            <button class="lb-nav lb-prev" onclick="navigateMedia(-1)">❯</button>
        </div>
        <div class="lb-footer">
            <div id="lb-counter" style="margin-bottom: 1rem; color: var(--text-muted); font-size: 0.8rem;">1 / 1</div>
            <div class="tag-manager" id="lb-tag-manager"></div>
            <div class="add-label-row" style="margin-top: 1rem; display: flex; gap: 0.5rem; justify-content: center; align-items: center;">
                <input type="text" id="lb-new-label" placeholder="Add custom label..." onkeydown="if(event.key==='Enter')addCustomLabel()" style="padding: 0.4rem 0.8rem; border-radius: 2rem; border: 1px solid var(--border-color); background: #1e293b; color: white; font-size: 0.8rem; max-width: 200px;">
                <button type="button" onclick="addCustomLabel()" class="tag-btn" style="padding: 0.4rem 1rem;">Add Label</button>
            </div>
        </div>
    </div>

<div id="poi-data" style="display:none">
''' + poi_html + '''
</div>

<script>
    const PASSWORD = "Naver#1390";
    const TAG_LIST = ['exterior', 'interior', 'license', 'opening hour', 'business card', 'menu', 'other'];
    const TAG_LABELS = { exterior: 'Exterior', interior: 'Interior', license: 'License', 'opening hour': 'Hours', 'business card': 'Card', menu: 'Menu', other: 'Other' };
    const LOCAL_TAGS_KEY = "alnafl_media_tags";
    const CUSTOM_TAGS_KEY = "alnafl_custom_tags";

    let currentPOIs = [];
    let activeFilter = 'all';
    let activeTagFilter = '';
    let searchQuery = '';

    let lbCurrentPOI = null;
    let lbCurrentMediaIdx = 0;
    let lbCurrentHref = '';

    function checkGate() {
        const input = document.getElementById('gate-password').value;
        if(input === PASSWORD) {
            sessionStorage.setItem('unlocked', 'true');
            document.getElementById('gate').classList.add('hidden');
        } else {
            document.getElementById('gate-error').style.display = 'block';
        }
    }

    if(sessionStorage.getItem('unlocked') === 'true') {
        document.getElementById('gate').classList.add('hidden');
    }

    function logout() {
        sessionStorage.removeItem('unlocked');
        location.reload();
    }

    function extractData() {
        const rawPois = Array.from(document.querySelectorAll('#poi-data .poi'));
        return rawPois.map((p, idx) => {
            let title = (p.querySelector('h3') || {}).innerText || '';
            const dashMatch = title.match(/[—–-]\\s*(.+)$/);
            if (dashMatch) title = dashMatch[1].trim();
            const meta = (p.querySelector('.meta') || {}).innerText || '';
            const mediaLinks = Array.from(p.querySelectorAll('.media-grid a')).map(a => ({
                href: a.getAttribute('href') || '',
                text: a.innerText || '',
                isPublic: a.classList.contains('public'),
                isVideo: a.classList.contains('video') || !!(a.getAttribute('href') || '').match(/\\.(mov|mp4)(\\?|$)/i)
            }));

            const hasMedia = p.dataset.media === "1";
            const category = meta.split('|')[0].trim() || '-';
            const status = meta.toLowerCase().includes('open') ? 'Open' : 'Closed';

            return { id: idx, title, category, status, hasMedia, mediaLinks };
        });
    }

    function optimizeCloudinary(url, width) {
        if (!url || !url.includes('cloudinary.com')) return url || '';
        return url.replace('/upload/', `/upload/w_${width || 600},f_auto,q_auto/`);
    }

    function carouselPrev(id) {
        const el = document.getElementById(id);
        if (!el) return;
        const itemW = el.offsetWidth;
        el.scrollBy({ left: -itemW, behavior: 'smooth' });
    }
    function carouselNext(id) {
        const el = document.getElementById(id);
        if (!el) return;
        const itemW = el.offsetWidth;
        el.scrollBy({ left: itemW, behavior: 'smooth' });
    }
    function updateCarouselIndicator(id) {
        const el = document.getElementById(id);
        const ind = document.getElementById(id + '-ind');
        if (!el || !ind) return;
        const idx = Math.round(el.scrollLeft / el.offsetWidth) + 1;
        const total = el.children.length;
        ind.textContent = idx + ' / ' + total;
    }

    function renderGrid() {
        const container = document.getElementById('poi-grid');
        const userTags = JSON.parse(localStorage.getItem(LOCAL_TAGS_KEY) || '{}');

        const filtered = currentPOIs.filter(p => {
            const matchesSearch = !searchQuery || p.title.toLowerCase().includes(searchQuery.toLowerCase()) || p.category.toLowerCase().includes(searchQuery.toLowerCase());
            const matchesGlobal = (activeFilter === 'all') || (activeFilter === 'media' && p.hasMedia) || (activeFilter === 'no-media' && !p.hasMedia);

            let matchesTag = true;
            if(activeTagFilter) {
                matchesTag = p.mediaLinks.some(m => m.href && m.href !== '#' && (userTags[m.href] || []).includes(activeTagFilter));
            }

            return matchesSearch && matchesGlobal && matchesTag;
        });

        container.innerHTML = filtered.map(p => {
            const mediaOnly = p.mediaLinks.filter(m => !m.isPublic && m.href && m.href !== '#');
            const photoCount = mediaOnly.filter(m => !m.isVideo).length;
            const videoCount = mediaOnly.filter(m => m.isVideo).length;
            const mediaCountLabel = photoCount && videoCount
                ? photoCount + ' photos, ' + videoCount + ' videos'
                : photoCount ? photoCount + ' photos' : videoCount ? videoCount + ' videos' : '';

            const galleryHtml = mediaOnly.map((m, i) => {
                const thumbUrl = m.isVideo ? '' : optimizeCloudinary(m.href, 400);
                return `
                <div class="gallery-item ${m.isVideo ? 'video' : ''}" onclick="openLightbox(${p.id}, ${i})">
                    ${thumbUrl ? `<img src="${thumbUrl}" loading="lazy">` : ''}
                </div>
            `;
            }).join('');

            const mapsLink = p.mediaLinks.find(m => m.href && m.href.includes('google.com/maps'));
            const carouselId = 'carousel-' + p.id;
            const hasMultiple = mediaOnly.length > 1;

            return `
                <div class="poi-card">
                    <div class="poi-gallery">
                    ${mediaOnly.length ? `
                        <div class="carousel-track" id="${carouselId}">${galleryHtml}</div>
                        ${hasMultiple ? `<button class="carousel-nav carousel-prev" onclick="carouselPrev('${carouselId}')">‹</button><button class="carousel-nav carousel-next" onclick="carouselNext('${carouselId}')">›</button>` : ''}
                        <span class="media-count">${mediaCountLabel}</span>
                        ${hasMultiple ? '<span class="carousel-indicator" id="' + carouselId + '-ind"></span>' : ''}
                    ` : '<div style="display: flex; align-items: center; justify-content: center; color: #475569; font-size: 0.8rem; height: 180px;">No media</div>'}
                    </div>
                    <div class="poi-info">
                        <h3>${p.title}</h3>
                        <div class="poi-tags">
                            <span class="chip category">${p.category}</span>
                            <span class="chip">${p.status}</span>
                        </div>
                    </div>
                    <div class="poi-footer">
                        ${mapsLink ? `<a href="${mapsLink.href}" target="_blank" class="maps-link">Google Maps →</a>` : '<span></span>'}
                    </div>
                </div>
            `;
        }).join('');

        document.getElementById('stat-pois').innerText = filtered.length;
        document.getElementById('stat-media').innerText = currentPOIs.reduce((s,p) => s + p.mediaLinks.filter(m => !m.isPublic && m.href && m.href !== '#').length, 0);

        document.querySelectorAll('.carousel-track').forEach(tr => {
            const ind = document.getElementById(tr.id + '-ind');
            if (ind) { ind.textContent = '1 / ' + tr.children.length; }
            tr.addEventListener('scroll', () => updateCarouselIndicator(tr.id));
        });
    }

    function handleSearch() {
        searchQuery = document.getElementById('search-input').value;
        renderGrid();
    }

    function setFilter(f) {
        activeFilter = f;
        document.querySelectorAll('.filter-btn[data-filter]').forEach(btn => btn.classList.toggle('active', btn.dataset.filter === f));
        renderGrid();
    }

    function setTagFilter(t) {
        activeTagFilter = t;
        document.querySelectorAll('.filter-btn[data-tag]').forEach(btn => btn.classList.toggle('active', btn.dataset.tag === t));
        renderGrid();
    }

    function openLightbox(poiId, mediaIdx) {
        const poi = currentPOIs.find(p => p.id === poiId);
        if(!poi) return;

        lbCurrentPOI = poi;
        lbCurrentMediaIdx = mediaIdx;

        document.getElementById('lightbox').classList.add('show');
        renderLightboxMedia();
    }

    function closeLightbox() {
        document.getElementById('lightbox').classList.remove('show');
        document.getElementById('lb-video').pause();
    }

    function navigateMedia(dir) {
        const media = lbCurrentPOI.mediaLinks.filter(m => !m.isPublic && m.href && m.href !== '#');
        lbCurrentMediaIdx = (lbCurrentMediaIdx + dir + media.length) % media.length;
        renderLightboxMedia();
    }

    function renderLightboxMedia() {
        const media = lbCurrentPOI.mediaLinks.filter(m => !m.isPublic && m.href && m.href !== '#');
        const current = media[lbCurrentMediaIdx];
        if (!current) return;

        document.getElementById('lb-title').innerText = lbCurrentPOI.title;
        document.getElementById('lb-counter').innerText = `${lbCurrentMediaIdx + 1} / ${media.length}`;

        const img = document.getElementById('lb-img');
        const vid = document.getElementById('lb-video');

        if(current.isVideo) {
            img.style.display = 'none';
            vid.style.display = 'block';
            vid.src = current.href.replace('/image/', '/video/');
            vid.play();
        } else {
            vid.style.display = 'none';
            img.style.display = 'block';
            img.src = optimizeCloudinary(current.href, 1200);
        }

        const userTags = JSON.parse(localStorage.getItem(LOCAL_TAGS_KEY) || '{}');
        const activeTags = userTags[current.href] || [];
        const customTags = JSON.parse(localStorage.getItem(CUSTOM_TAGS_KEY) || '[]');
        const allTags = TAG_LIST.concat(customTags);

        lbCurrentHref = current.href;
        document.getElementById('lb-tag-manager').innerHTML = allTags.map(tag => `
            <button class="tag-btn ${activeTags.includes(tag) ? 'active' : ''}" onclick="toggleTag(lbCurrentHref, '${tag.replace(/'/g, "\\\\'")}')">${TAG_LABELS[tag] || tag}</button>
        `).join('');
    }

    function addCustomLabel() {
        const input = document.getElementById('lb-new-label');
        const label = (input.value || '').trim().toLowerCase();
        if (!label || !lbCurrentHref) return;
        let customTags = JSON.parse(localStorage.getItem(CUSTOM_TAGS_KEY) || '[]');
        if (!customTags.includes(label)) {
            customTags.push(label);
            customTags.sort();
            localStorage.setItem(CUSTOM_TAGS_KEY, JSON.stringify(customTags));
        }
        toggleTag(lbCurrentHref, label);
        input.value = '';
        refreshTagFilters();
    }

    function refreshTagFilters() {
        const container = document.getElementById('tag-filters');
        container.innerHTML = '<button class="filter-btn" data-tag="" onclick="setTagFilter(\\'\\')">All tags</button>';
        const customTags = JSON.parse(localStorage.getItem(CUSTOM_TAGS_KEY) || '[]');
        TAG_LIST.concat(customTags).forEach(t => {
            const btn = document.createElement('button');
            btn.className = 'filter-btn';
            btn.dataset.tag = t;
            btn.innerText = TAG_LABELS[t] || t;
            btn.onclick = () => setTagFilter(t);
            container.appendChild(btn);
        });
    }

    function toggleTag(href, tag) {
        if (!href) return;
        let userTags = JSON.parse(localStorage.getItem(LOCAL_TAGS_KEY) || '{}');
        let tags = userTags[href] || [];

        if(tags.includes(tag)) {
            tags = tags.filter(t => t !== tag);
        } else {
            tags.push(tag);
        }

        userTags[href] = tags;
        localStorage.setItem(LOCAL_TAGS_KEY, JSON.stringify(userTags));
        renderLightboxMedia();
        renderGrid();
    }

    window.onload = () => {
        currentPOIs = extractData();
        refreshTagFilters();
        renderGrid();
    };

    document.getElementById('gate-password').onkeydown = (e) => { if (e.key === 'Enter') checkGate(); };

    document.addEventListener('keydown', (e) => {
        if(!document.getElementById('lightbox').classList.contains('show')) return;
        if(e.key === "ArrowRight") navigateMedia(1);
        if(e.key === "ArrowLeft") navigateMedia(-1);
        if(e.key === "Escape") closeLightbox();
    });
</script>

</body>
</html>
'''

with open('alnafl_media_review.html', 'w', encoding='utf-8') as f:
    f.write(template)

print('Built enhanced alnafl_media_review.html')
