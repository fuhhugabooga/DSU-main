/* =========================================
   NETWORK 2 — D3 bipartite graph: ONG <-> ISU
   (operational collaborations: pandemic + refugee crisis)
   ========================================= */

import {
    loadNetwork2Data, ACTOR_TYPES, NET2_CONTEXTS,
    getActorLabel
} from './data.js';

let net2Data = null;
let svg, g, linkGroup, nodeGroup, labelGroup;
let zoomBehavior = null;
let simulation = null;
let width, height;
let currentNodes = [];
let currentLinks = [];
let linkSel = null, nodeSel = null, labelSel = null;
let selectedNodeId = null;
let initialized = false;
let firstRender = true;
let pendingFit = false;

// Filter state — which contexts (crises) are visible
let activeContexts = new Set(Object.keys(NET2_CONTEXTS));

// ---- PUBLIC API ----

export async function initNetwork2() {
    if (initialized) return;
    initialized = true;

    net2Data = await loadNetwork2Data();

    setupSVG();
    buildControls();
    buildLegend();
    setupToolbar();
    rebuildGraph();

    window.addEventListener('resize', () => {
        if (!isActive()) return;
        resizeSVG();
        if (simulation) simulation.alpha(0.3).restart();
    });
}

function isActive() {
    return document.getElementById('page-network2')?.classList.contains('active');
}

// ---- SVG SETUP ----

function setupSVG() {
    const container = document.getElementById('graph-container2');
    width = container.clientWidth || 800;
    height = container.clientHeight || 600;

    // Let CSS own the SVG size (width/height:100%); keep width/height vars
    // only for the force-center math, re-measured on resize.
    svg = d3.select('#network2-svg');
    svg.selectAll('*').remove();

    const defs = svg.append('defs');
    const filter = defs.append('filter').attr('id', 'glow2');
    filter.append('feGaussianBlur').attr('stdDeviation', '3').attr('result', 'coloredBlur');
    const merge = filter.append('feMerge');
    merge.append('feMergeNode').attr('in', 'coloredBlur');
    merge.append('feMergeNode').attr('in', 'SourceGraphic');

    g = svg.append('g').attr('class', 'graph-group');
    linkGroup = g.append('g').attr('class', 'links');
    nodeGroup = g.append('g').attr('class', 'nodes');
    labelGroup = g.append('g').attr('class', 'labels');

    zoomBehavior = d3.zoom()
        .scaleExtent([0.15, 5])
        .on('zoom', (event) => g.attr('transform', event.transform));
    svg.call(zoomBehavior);

    svg.on('click', (event) => {
        if (event.target === svg.node()) deselectNode();
    });
}

function resizeSVG() {
    const container = document.getElementById('graph-container2');
    width = container.clientWidth || width;
    height = container.clientHeight || height;
}

// Called by app.js when the page becomes visible (container now has a size)
export function resizeNetwork2() {
    if (!initialized || !svg) return;
    resizeSVG();
    if (simulation) simulation.alpha(0.3).restart();
}

// ---- GRAPH BUILDING ----

function rebuildGraph() {
    const { nodes, edges } = net2Data;

    // Visible ONGs = those whose context is enabled
    const visibleOng = new Set();
    for (const [id, node] of Object.entries(nodes)) {
        if (node.type === 'ONG' && activeContexts.has(node.context)) {
            visibleOng.add(id);
        }
    }

    // Active edges + connected ISU hubs
    const activeEdges = [];
    const visibleIsu = new Set();
    for (const edge of edges) {
        if (!visibleOng.has(edge.source)) continue;
        activeEdges.push(edge);
        visibleIsu.add(edge.target);
    }

    const d3Nodes = [];
    const nodeMap = new Map();

    for (const id of visibleIsu) {
        const n = nodes[id];
        const d3Node = { id, label: n.label, type: 'ISU', color: n.color, radius: 16, data: n };
        d3Nodes.push(d3Node);
        nodeMap.set(id, d3Node);
    }

    for (const id of visibleOng) {
        const n = nodes[id];
        // size by Nr_colaborari (sqrt scale, clamped)
        const r = Math.max(5, Math.min(18, 4 + Math.sqrt(n.nrColaborari) * 2.5));
        const fullLabel = n.label;
        const d3Node = {
            id,
            label: fullLabel.length > 26 ? fullLabel.substring(0, 23) + '…' : fullLabel,
            fullLabel,
            type: 'ONG',
            color: n.color,
            radius: r,
            data: n
        };
        d3Nodes.push(d3Node);
        nodeMap.set(id, d3Node);
    }

    const d3Links = activeEdges
        .filter(e => nodeMap.has(e.source) && nodeMap.has(e.target))
        .map(e => ({ source: e.source, target: e.target }));

    currentNodes = d3Nodes;
    currentLinks = d3Links;

    updateStats(visibleOng.size, visibleIsu.size, sumColaborari(visibleOng), d3Links.length);
    updateEmptyMessage(visibleOng.size);
    pendingFit = true;
    renderGraph(d3Nodes, d3Links);
}

function sumColaborari(visibleOng) {
    let total = 0;
    for (const id of visibleOng) total += net2Data.nodes[id].nrColaborari || 0;
    return total;
}

function renderGraph(nodes, links) {
    if (simulation) simulation.stop();
    const animate = !firstRender;

    linkGroup.selectAll('*').remove();
    nodeGroup.selectAll('*').remove();
    labelGroup.selectAll('*').remove();

    if (nodes.length === 0) { firstRender = false; return; }

    linkSel = linkGroup.selectAll('line')
        .data(links)
        .join('line')
        .attr('stroke', 'rgba(220, 38, 38, 0.12)')
        .attr('stroke-width', 1.2);

    nodeSel = nodeGroup.selectAll('g')
        .data(nodes, d => d.id)
        .join('g')
        .attr('class', 'node-group')
        .style('cursor', 'pointer');

    // ISU hubs = diamonds
    nodeSel.filter(d => d.type === 'ISU')
        .append('rect')
        .attr('width', d => d.radius * 1.6)
        .attr('height', d => d.radius * 1.6)
        .attr('x', d => -d.radius * 0.8)
        .attr('y', d => -d.radius * 0.8)
        .attr('rx', 3)
        .attr('transform', 'rotate(45)')
        .attr('fill', d => d.color)
        .attr('stroke', 'rgba(255,255,255,0.35)')
        .attr('stroke-width', 1.5);

    // ONG = circles colored by actor type, sized by collaborations
    nodeSel.filter(d => d.type === 'ONG')
        .append('circle')
        .attr('r', d => d.radius)
        .attr('fill', d => d.color)
        .attr('stroke', 'rgba(255,255,255,0.2)')
        .attr('stroke-width', 1);

    labelSel = labelGroup.selectAll('text')
        .data(nodes, d => d.id)
        .join('text')
        .text(d => d.type === 'ISU' ? d.label : (d.label.length > 18 ? d.label.substring(0, 16) + '…' : d.label))
        .attr('text-anchor', 'middle')
        .attr('dy', d => d.type === 'ISU' ? d.radius + 16 : d.radius + 12)
        .attr('fill', '#cbd5e1')
        .attr('font-size', d => d.type === 'ISU' ? '12px' : '8.5px')
        .attr('font-weight', d => d.type === 'ISU' ? '700' : '400')
        .attr('font-family', 'Nunito, Inter, sans-serif')
        .attr('pointer-events', 'none')
        // hide ONG labels by default to avoid clutter; show ISU codes
        .style('display', d => d.type === 'ISU' ? null : 'none');

    if (animate) {
        linkSel.style('opacity', 0).transition().duration(300).style('opacity', 1);
        nodeSel.style('opacity', 0).transition().duration(400).style('opacity', 1);
    }
    firstRender = false;

    const tooltip = document.getElementById('tooltip2');
    const isMobile = () => window.innerWidth < 768 || 'ontouchstart' in window;

    nodeSel.on('mouseenter', function (event, d) {
        if (isMobile()) return;
        highlightConnections(d);
        showTooltip(event, d, tooltip);
    })
    .on('mousemove', (event) => { if (!isMobile()) moveTooltip(event, tooltip); })
    .on('mouseleave', function () {
        if (isMobile()) return;
        if (selectedNodeId) {
            const sel = currentNodes.find(n => n.id === selectedNodeId);
            if (sel) highlightConnections(sel); else resetHighlight();
        } else {
            resetHighlight();
        }
        hideTooltip(tooltip);
    })
    .on('click', function (event, d) {
        event.stopPropagation();
        if (isMobile()) hideTooltip(tooltip);
        selectNode(d);
    });

    nodeSel.call(d3.drag()
        .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x; d.fy = d.y;
        })
        .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null; d.fy = null;
        }));

    resizeSVG(); // ensure width/height reflect the current container size
    const mobile = window.innerWidth < 768;
    simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(mobile ? 60 : 90))
        .force('charge', d3.forceManyBody().strength(mobile ? -90 : -170))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(d => d.radius + (d.type === 'ISU' ? 22 : 6)))
        .force('x', d3.forceX(width / 2).strength(0.04))
        .force('y', d3.forceY(height / 2).strength(0.04))
        .alpha(1)
        .alphaDecay(0.022)
        .on('tick', () => {
            linkSel
                .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
            nodeSel.attr('transform', d => `translate(${d.x},${d.y})`);
            labelSel.attr('x', d => d.x).attr('y', d => d.y);
        });

    // Fit the graph once, after the layout has had time to spread out.
    // (Not tied to simulation 'end' so dragging a node doesn't reset the view.)
    setTimeout(() => {
        if (pendingFit && !selectedNodeId) {
            zoomReset();
            pendingFit = false;
        }
    }, 1200);
}

// ---- HIGHLIGHT ----

function connectedIdSet(d) {
    const ids = new Set([d.id]);
    currentLinks.forEach(l => {
        const s = typeof l.source === 'object' ? l.source.id : l.source;
        const t = typeof l.target === 'object' ? l.target.id : l.target;
        if (s === d.id) ids.add(t);
        if (t === d.id) ids.add(s);
    });
    return ids;
}

function highlightConnections(d) {
    if (!nodeSel) return;
    const ids = connectedIdSet(d);

    nodeSel.transition().duration(150).style('opacity', n => ids.has(n.id) ? 1 : 0.08);
    labelSel.transition().duration(150)
        .style('opacity', n => ids.has(n.id) ? 1 : 0.05)
        // reveal ONG labels for connected nodes
        .style('display', n => (n.type === 'ISU' || ids.has(n.id)) ? null : 'none');

    linkSel.transition().duration(150)
        .attr('stroke', l => {
            const s = typeof l.source === 'object' ? l.source.id : l.source;
            const t = typeof l.target === 'object' ? l.target.id : l.target;
            return (s === d.id || t === d.id) ? 'rgba(220, 38, 38, 0.6)' : 'rgba(220, 38, 38, 0.02)';
        })
        .attr('stroke-width', l => {
            const s = typeof l.source === 'object' ? l.source.id : l.source;
            const t = typeof l.target === 'object' ? l.target.id : l.target;
            return (s === d.id || t === d.id) ? 2.2 : 0.5;
        });

    nodeSel.filter(n => n.id === d.id).select('circle, rect')
        .transition().duration(150)
        .attr('stroke', '#fff').attr('stroke-width', 2.5)
        .style('filter', 'url(#glow2)');
}

function resetHighlight() {
    if (!nodeSel) return;
    nodeSel.transition().duration(200).style('opacity', 1);
    labelSel.transition().duration(200)
        .style('opacity', 1)
        .style('display', n => n.type === 'ISU' ? null : 'none');
    linkSel.transition().duration(200)
        .attr('stroke', 'rgba(220, 38, 38, 0.12)').attr('stroke-width', 1.2);
    nodeSel.selectAll('circle').transition().duration(200)
        .attr('stroke', 'rgba(255,255,255,0.2)').attr('stroke-width', 1).style('filter', null);
    nodeSel.selectAll('rect').transition().duration(200)
        .attr('stroke', 'rgba(255,255,255,0.35)').attr('stroke-width', 1.5).style('filter', null);
}

// ---- ZOOM ----

function zoomToFocus(d) {
    if (!zoomBehavior || !svg) return;
    const ids = connectedIdSet(d);
    const ns = currentNodes.filter(n => ids.has(n.id) && n.x !== undefined);
    if (ns.length === 0) return;
    fitTo(ns, 100, 2.5);
}

function zoomReset() {
    const positioned = currentNodes.filter(n => n.x !== undefined);
    if (positioned.length === 0) return;
    fitTo(positioned, 60, 1);
}

function fitTo(ns, padding, maxScale) {
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    ns.forEach(n => {
        minX = Math.min(minX, n.x); maxX = Math.max(maxX, n.x);
        minY = Math.min(minY, n.y); maxY = Math.max(maxY, n.y);
    });
    minX -= padding; maxX += padding; minY -= padding; maxY += padding;
    const dx = maxX - minX, dy = maxY - minY;
    const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
    const scale = Math.min(width / dx, height / dy, maxScale);
    const tx = width / 2 - cx * scale, ty = height / 2 - cy * scale;
    svg.transition().duration(700).ease(d3.easeCubicInOut)
        .call(zoomBehavior.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
}

// ---- TOOLTIP ----

function showTooltip(event, d, el) {
    let html = `<div class="tooltip-name">${escapeHtml(d.data.label)}</div>`;
    if (d.type === 'ONG') {
        html += `<div class="tooltip-type">${getActorLabel(d.data.tipActor)}</div>`;
        html += `<div class="tooltip-connections">${d.data.nrColaborari} colaborări · ${d.data.nrISU} județe</div>`;
        if (d.data.context) {
            const c = NET2_CONTEXTS[d.data.context];
            html += `<div style="color:${c ? c.color : '#94a3b8'};font-size:0.72rem">${d.data.context}</div>`;
        }
    } else {
        const partners = net2Data.edges.filter(e => e.target === d.id).length;
        html += `<div class="tooltip-type">ISU ${escapeHtml(d.data.fullName)}</div>`;
        html += `<div class="tooltip-connections">${partners} ONG-uri colaboratoare</div>`;
    }
    el.innerHTML = html;
    el.classList.remove('hidden');
    moveTooltip(event, el);
}

function moveTooltip(event, el) {
    const rect = document.getElementById('graph-container2').getBoundingClientRect();
    let x = event.clientX - rect.left + 14;
    let y = event.clientY - rect.top - 10;
    if (x + 260 > rect.width) x = event.clientX - rect.left - 260;
    if (y + 100 > rect.height) y = event.clientY - rect.top - 100;
    el.style.left = x + 'px';
    el.style.top = y + 'px';
}

function hideTooltip(el) { el.classList.add('hidden'); }

// ---- SELECTION / DETAIL CARD ----

function selectNode(d) {
    selectedNodeId = d.id;
    showDetailCard(d);
    highlightConnections(d);
    zoomToFocus(d);
}

function deselectNode() {
    selectedNodeId = null;
    document.getElementById('partner-detail2')?.classList.add('hidden');
    resetHighlight();
    zoomReset();
}

function showDetailCard(d) {
    const detail = document.getElementById('partner-detail2');
    const content = document.getElementById('detail-content2');
    const { nodes, edges } = net2Data;
    let html = '';

    if (d.type === 'ONG') {
        const n = d.data;
        html += `<div class="detail-name">${escapeHtml(n.label)}</div>`;
        html += `<div class="detail-type">${getActorLabel(n.tipActor)}</div>`;

        let badges = '';
        if (n.context) {
            const c = NET2_CONTEXTS[n.context];
            const col = c ? c.color : '#94a3b8';
            badges += `<span class="badge" style="background:${col}22;color:${col};border:1px solid ${col}55">${escapeHtml(n.context)}</span>`;
        }
        badges += `<span class="badge badge-strategic">${n.nrColaborari} colaborări</span>`;
        html += `<div class="detail-badges">${badges}</div>`;

        html += `<div class="detail-desc">${escapeHtml(n.description)}</div>`;

        const myIsu = edges.filter(e => e.source === d.id)
            .map(e => nodes[e.target])
            .filter(Boolean);
        html += `<div class="detail-domains-label">Județe acoperite (${myIsu.length})</div>`;
        html += `<div class="detail-domains">`;
        myIsu.sort((a, b) => a.label.localeCompare(b.label)).forEach(isu => {
            html += `<span class="tag-domain" title="${escapeHtml(isu.fullName)}">${escapeHtml(isu.label)}</span>`;
        });
        html += `</div>`;
    } else {
        const n = d.data;
        const partners = edges.filter(e => e.target === d.id)
            .map(e => nodes[e.source]).filter(Boolean);
        html += `<div class="detail-name">ISU ${escapeHtml(n.fullName)}</div>`;
        html += `<div class="detail-type">Inspectorat pentru Situații de Urgență (${escapeHtml(n.label)})</div>`;
        html += `<div class="domain-partner-count">Au colaborat operațional <strong>${partners.length}</strong> ONG-uri în acest județ.</div>`;
        if (partners.length > 0) {
            html += `<div class="detail-domains-label" style="margin-top:12px">ONG-uri colaboratoare</div>`;
            html += `<div class="detail-domains">`;
            partners.sort((a, b) => a.label.localeCompare(b.label)).forEach(p => {
                html += `<span class="tag-domain">${escapeHtml(p.label)}</span>`;
            });
            html += `</div>`;
        }
    }

    content.innerHTML = html;
    detail.classList.remove('hidden');
}

// ---- CONTROLS (search + context filter) ----

function buildControls() {
    // Context filter chips
    const chipWrap = document.getElementById('net2-context-chips');
    if (chipWrap) {
        let html = '';
        for (const [key, cfg] of Object.entries(NET2_CONTEXTS)) {
            html += `<button class="net2-chip active" data-context="${escapeHtml(key)}" style="--chip-color:${cfg.color}">
                <span class="net2-chip-dot"></span>${escapeHtml(cfg.label)}
            </button>`;
        }
        chipWrap.innerHTML = html;
        chipWrap.querySelectorAll('.net2-chip').forEach(btn => {
            btn.addEventListener('click', () => {
                const ctx = btn.dataset.context;
                if (activeContexts.has(ctx)) {
                    // Don't allow disabling the last active chip
                    if (activeContexts.size === 1) return;
                    activeContexts.delete(ctx);
                    btn.classList.remove('active');
                } else {
                    activeContexts.add(ctx);
                    btn.classList.add('active');
                }
                deselectNode();
                rebuildGraph();
            });
        });
    }

    // Search
    const input = document.getElementById('net2-search');
    const resultsEl = document.getElementById('net2-search-results');
    if (input && resultsEl) {
        const ongs = Object.entries(net2Data.nodes)
            .filter(([, n]) => n.type === 'ONG')
            .map(([id, n]) => ({ id, label: n.label }))
            .sort((a, b) => a.label.localeCompare(b.label));

        input.addEventListener('input', () => {
            const q = input.value.toLowerCase().trim();
            if (q.length < 2) { resultsEl.classList.add('hidden'); return; }
            const matches = ongs.filter(o => o.label.toLowerCase().includes(q)).slice(0, 10);
            if (matches.length === 0) {
                resultsEl.innerHTML = '<div class="search-result-item" style="color:var(--text-dim)">Niciun rezultat</div>';
                resultsEl.classList.remove('hidden');
                return;
            }
            resultsEl.innerHTML = matches.map(m =>
                `<div class="search-result-item" data-id="${m.id}">${escapeHtml(m.label)}</div>`).join('');
            resultsEl.classList.remove('hidden');
            resultsEl.querySelectorAll('.search-result-item[data-id]').forEach(item => {
                item.addEventListener('click', () => {
                    const node = currentNodes.find(n => n.id === item.dataset.id);
                    if (node) {
                        selectNode(node);
                    } else {
                        // ONG hidden by current context filter — enable all and retry
                        activeContexts = new Set(Object.keys(NET2_CONTEXTS));
                        document.querySelectorAll('#net2-context-chips .net2-chip').forEach(b => b.classList.add('active'));
                        rebuildGraph();
                        setTimeout(() => {
                            const n2 = currentNodes.find(n => n.id === item.dataset.id);
                            if (n2) selectNode(n2);
                        }, 200);
                    }
                    input.value = '';
                    resultsEl.classList.add('hidden');
                });
            });
        });

        document.addEventListener('click', (e) => {
            if (!resultsEl.contains(e.target) && e.target !== input) resultsEl.classList.add('hidden');
        });
    }
}

// ---- LEGEND ----

function buildLegend() {
    const panel = document.getElementById('legend-panel2');
    if (!panel) return;

    // Only show actor types that actually appear in the data
    const present = new Set(Object.values(net2Data.nodes).filter(n => n.type === 'ONG').map(n => n.tipActor));

    let html = '<div class="legend-section-title">Tip organizație</div>';
    for (const [key, cfg] of Object.entries(ACTOR_TYPES)) {
        if (!present.has(key)) continue;
        html += `<div class="legend-item"><span class="legend-dot" style="background:${cfg.color}"></span><span>${cfg.label}</span></div>`;
    }
    html += '<div class="legend-item"><span class="legend-diamond"></span><span>ISU județean (hub)</span></div>';
    html += '<div class="legend-section-title" style="margin-top:8px">Mărimea nodului = nr. colaborări</div>';
    panel.innerHTML = html;
}

// ---- TOOLBAR ----

function setupToolbar() {
    document.getElementById('net2-reset-btn')?.addEventListener('click', () => {
        deselectNode();
        zoomReset();
    });

    const legendToggle = document.getElementById('legend-toggle2');
    const legendPanel = document.getElementById('legend-panel2');
    if (legendToggle && legendPanel) {
        legendToggle.addEventListener('click', () => legendPanel.classList.toggle('hidden'));
    }

    document.getElementById('close-detail2')?.addEventListener('click', deselectNode);

    document.addEventListener('keydown', (e) => {
        if (!isActive()) return;
        if (e.key === 'Escape') {
            if (selectedNodeId) deselectNode();
            document.getElementById('net2-search-results')?.classList.add('hidden');
        }
    });
}

// ---- STATS / EMPTY ----

function updateStats(ong, isu, colab, conn) {
    setText('n2-stat-ong', ong);
    setText('n2-stat-isu', isu);
    setText('n2-stat-colab', colab);
    setText('n2-stat-conn', conn);
}

function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = typeof val === 'number' ? val.toLocaleString('ro-RO') : val;
}

function updateEmptyMessage(count) {
    let msg = document.getElementById('empty-graph-msg2');
    if (count === 0) {
        if (!msg) {
            msg = document.createElement('div');
            msg.id = 'empty-graph-msg2';
            msg.className = 'empty-graph-msg';
            msg.innerHTML = `
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/><path d="M8 11h6"/></svg>
                <div class="empty-graph-title">Nu există niciun ONG</div>
                <div class="empty-graph-text">Verifică filtrele de context selectate.</div>`;
            document.getElementById('graph-container2').appendChild(msg);
        }
        msg.style.display = 'flex';
    } else if (msg) {
        msg.style.display = 'none';
    }
}

// ---- UTIL ----

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}
