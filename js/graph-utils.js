/* =========================================
   SHARED HELPERS for the two D3 network views
   (network.js — partners ↔ domains, network2.js — ONG ↔ ISU)
   ========================================= */

// Honoured by the JS-driven entrance/count-up animations (CSS animations are
// already disabled globally via the media query in app.css).
export const REDUCED_MOTION =
    window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Consistent feather-style inline icon set (rounded caps/joins).
// Usage: icons.help({ size: 14 })
const svgIcon = (paths, { size = 16, filled = false } = {}) =>
    `<svg width="${size}" height="${size}" viewBox="0 0 24 24" aria-hidden="true" ` +
    (filled
        ? 'fill="currentColor" stroke="none">'
        : 'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">') +
    paths + '</svg>';

export const icons = {
    reset:    o => svgIcon('<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9z"/><polyline points="9 22 9 12 15 12 15 22"/>', o),
    download: o => svgIcon('<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>', o),
    image:    o => svgIcon('<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/>', o),
    help:     o => svgIcon('<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>', o),
    analysis: o => svgIcon('<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>', o),
    chevron:  o => svgIcon('<polyline points="9 18 15 12 9 6"/>', o),
    star:     o => svgIcon('<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>', { ...o, filled: true })
};

// Escape user/CSV-provided strings before injecting them into innerHTML
export function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// Shorten long labels with an ellipsis
export function truncate(str, max) {
    return str.length > max ? str.substring(0, max - 2) + '…' : str;
}

// Animate a numeric stat from 0 to its target value (ease-out cubic)
export function countUp(el, target, duration = 900) {
    if (!el) return;
    if (REDUCED_MOTION || !Number.isFinite(target)) {
        el.textContent = Number(target).toLocaleString('ro-RO');
        return;
    }
    const start = performance.now();
    const tick = now => {
        const p = Math.min(1, (now - start) / duration);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(target * eased).toLocaleString('ro-RO');
        if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
}

// Position a cursor-following tooltip, flipped when near the container edges
export function moveTooltip(event, el, container) {
    const rect = container.getBoundingClientRect();
    let x = event.clientX - rect.left + 14;
    let y = event.clientY - rect.top - 10;
    if (x + 260 > rect.width) x = event.clientX - rect.left - 260;
    if (y + 100 > rect.height) y = event.clientY - rect.top - 100;
    el.style.left = x + 'px';
    el.style.top = y + 'px';
}

// Compute the d3.zoom transform that fits the given (positioned) nodes into a
// width×height viewport. offsetX shifts the focus left so a cluster is not
// hidden behind the right-docked detail panel on desktop. Returns null when
// there is nothing to fit (caller should skip the transition).
export function fitTransform(nodes, width, height, { padding = 60, maxScale = 1, offsetX = 0 } = {}) {
    const positioned = nodes.filter(n => n.x !== undefined);
    if (positioned.length === 0 || !width || !height) return null;

    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    positioned.forEach(n => {
        minX = Math.min(minX, n.x); maxX = Math.max(maxX, n.x);
        minY = Math.min(minY, n.y); maxY = Math.max(maxY, n.y);
    });
    minX -= padding; maxX += padding;
    minY -= padding; maxY += padding;

    const scale = Math.min(width / (maxX - minX), height / (maxY - minY), maxScale);
    if (!isFinite(scale) || scale <= 0) return null;

    const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
    return d3.zoomIdentity
        .translate(width / 2 - offsetX - cx * scale, height / 2 - cy * scale)
        .scale(scale);
}

// ---- EXPORT (SVG / PNG) ----

function serializeSvg(svgNode, width, height) {
    const clone = svgNode.cloneNode(true);
    clone.setAttribute('width', width);
    clone.setAttribute('height', height);

    const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    bg.setAttribute('width', width);
    bg.setAttribute('height', height);
    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    bg.setAttribute('fill', isDark ? '#0a0e1a' : '#f8fafc');
    clone.insertBefore(bg, clone.firstChild);

    // Fonts are not embedded in the export, so give text a safe fallback
    clone.querySelectorAll('text').forEach(el => {
        if (!el.style.fontFamily) el.style.fontFamily = 'sans-serif';
    });

    return '<?xml version="1.0" encoding="UTF-8"?>' + new XMLSerializer().serializeToString(clone);
}

function triggerDownload(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// Serialize an SVG with a solid dark background and trigger a download
export function downloadSvg(svgNode, width, height, filename) {
    const svgString = serializeSvg(svgNode, width, height);
    const url = URL.createObjectURL(new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' }));
    triggerDownload(url, filename);
}

// Rasterize the SVG onto a canvas (2× for sharpness) and download as PNG
export function downloadPng(svgNode, width, height, filename, scale = 2) {
    const svgString = serializeSvg(svgNode, width, height);
    const url = URL.createObjectURL(new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' }));
    const img = new Image();
    img.onload = () => {
        URL.revokeObjectURL(url);
        const canvas = document.createElement('canvas');
        canvas.width = Math.round(width * scale);
        canvas.height = Math.round(height * scale);
        canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(blob => {
            if (blob) triggerDownload(URL.createObjectURL(blob), filename);
        }, 'image/png');
    };
    img.src = url;
}
