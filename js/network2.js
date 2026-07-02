/* =========================================
   NETWORK 2 — D3 bipartite graph: ONG <-> ISU
   (operational collaborations: pandemic + refugee crisis)
   ========================================= */

import {
    loadNetwork2Data, ACTOR_TYPES, NET2_CONTEXTS,
    getActorLabel
} from './data.js';
import {
    escapeHtml, truncate, moveTooltip, fitTransform,
    downloadSvg, downloadPng, icons, countUp, REDUCED_MOTION
} from './graph-utils.js';
import { betweennessCentrality, degreeMap } from './metrics.js';

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
    buildAnalysisPanel();
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
        const d3Node = { id, label: n.label, type: 'ISU', color: n.color, radius: 19, data: n };
        d3Nodes.push(d3Node);
        nodeMap.set(id, d3Node);
    }

    for (const id of visibleOng) {
        const n = nodes[id];
        // size by Nr_colaborari (sqrt scale, clamped)
        const r = Math.max(5, Math.min(18, 4 + Math.sqrt(n.nrColaborari) * 2.5));
        const d3Node = {
            id,
            label: truncate(n.label, 26),
            fullLabel: n.label,
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
        .map(e => {
            const ctx = nodes[e.source]?.context;
            return {
                source: e.source,
                target: e.target,
                context: ctx,
                color: NET2_CONTEXTS[ctx]?.color || '#dc2626'
            };
        });

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
    resizeSVG(); // ensure width/height reflect the current container size
    const animate = !firstRender;

    linkGroup.selectAll('*').remove();
    nodeGroup.selectAll('*').remove();
    labelGroup.selectAll('*').remove();

    if (nodes.length === 0) { firstRender = false; return; }

    linkSel = linkGroup.selectAll('line')
        .data(links)
        .join('line')
        .attr('stroke', d => d.color)
        .attr('stroke-opacity', 0.4)
        .attr('stroke-width', 1.4);

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
        .text(d => d.type === 'ISU' ? d.label : truncate(d.label, 18))
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
    } else {
        // First render: seed everything at the center so the layout "blooms"
        // outward while the nodes fade in, staggered.
        nodes.forEach(n => {
            n.x = width / 2 + (Math.random() - 0.5) * 30;
            n.y = height / 2 + (Math.random() - 0.5) * 30;
        });
        if (!REDUCED_MOTION) {
            nodeSel.style('opacity', 0).transition()
                .duration(450).delay((d, i) => 100 + i * 2.5).style('opacity', 1);
            linkSel.style('opacity', 0).transition()
                .duration(800).delay(450).style('opacity', 1);
        }
    }
    firstRender = false;

    const tooltip = document.getElementById('tooltip2');
    const isMobile = () => window.innerWidth < 768 || 'ontouchstart' in window;

    nodeSel.on('mouseenter', function (event, d) {
        if (isMobile()) return;
        highlightConnections(d);
        showTooltip(event, d, tooltip);
    })
    .on('mousemove', (event) => { if (!isMobile()) moveTooltip(event, tooltip, graphContainer()); })
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

    const mobile = window.innerWidth < 768;
    simulation = d3.forceSimulation(nodes)
        // ONGs sit close to their hub; hubs repel each other strongly so the
        // county clusters spread out and overlap less.
        .force('link', d3.forceLink(links).id(d => d.id).distance(mobile ? 55 : 75).strength(0.6))
        .force('charge', d3.forceManyBody().strength(d => d.type === 'ISU' ? (mobile ? -260 : -520) : (mobile ? -60 : -110)))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(d => d.radius + (d.type === 'ISU' ? 30 : 4)))
        .force('x', d3.forceX(width / 2).strength(0.03))
        .force('y', d3.forceY(height / 2).strength(0.03))
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

    nodeSel.transition().duration(150).style('opacity', n => ids.has(n.id) ? 1 : 0.04);
    labelSel.transition().duration(150)
        .style('opacity', n => ids.has(n.id) ? 1 : 0.03)
        // reveal ONG labels for connected nodes
        .style('display', n => (n.type === 'ISU' || ids.has(n.id)) ? null : 'none');

    const isLinked = l => {
        const s = typeof l.source === 'object' ? l.source.id : l.source;
        const t = typeof l.target === 'object' ? l.target.id : l.target;
        return s === d.id || t === d.id;
    };
    linkSel.transition().duration(150)
        .attr('stroke', l => l.color) // keep context color, vary opacity for emphasis
        .attr('stroke-opacity', l => isLinked(l) ? 0.8 : 0.03)
        .attr('stroke-width', l => isLinked(l) ? 2.2 : 0.5);

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
        .attr('stroke', l => l.color).attr('stroke-opacity', 0.4).attr('stroke-width', 1.4);
    nodeSel.selectAll('circle').transition().duration(200)
        .attr('stroke', 'rgba(255,255,255,0.2)').attr('stroke-width', 1).style('filter', null);
    nodeSel.selectAll('rect').transition().duration(200)
        .attr('stroke', 'rgba(255,255,255,0.35)').attr('stroke-width', 1.5).style('filter', null);
}

// ---- ZOOM ----

function graphContainer() {
    return document.getElementById('graph-container2');
}

function zoomToFocus(d) {
    const ids = connectedIdSet(d);
    // Bias left so the cluster isn't hidden behind the right-docked detail panel.
    const offsetX = window.innerWidth >= 768 ? 196 : 0;
    fitTo(currentNodes.filter(n => ids.has(n.id)), { padding: 100, maxScale: 2.5, offsetX });
}

function zoomReset() {
    fitTo(currentNodes, { padding: 50, maxScale: 1.3 });
}

function fitTo(ns, opts) {
    if (!zoomBehavior || !svg) return;
    const transform = fitTransform(ns, width, height, opts);
    if (!transform) return;
    svg.transition().duration(700).ease(d3.easeCubicInOut)
        .call(zoomBehavior.transform, transform);
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
    moveTooltip(event, el, graphContainer());
}

function hideTooltip(el) { el.classList.add('hidden'); }

// ---- SELECTION / DETAIL CARD ----

function selectNode(d) {
    selectedNodeId = d.id;
    showDetailCard(d);
    highlightConnections(d);
    zoomToFocus(d);

    // Deep-link the selection so it can be shared
    const key = d.data?.label;
    if (key) history.replaceState(null, '', '#network2/' + encodeURIComponent(key));
}

function deselectNode() {
    selectedNodeId = null;
    document.getElementById('partner-detail2')?.classList.add('hidden');
    resetHighlight();
    zoomReset();
    if (isActive()) history.replaceState(null, '', '#network2');
}

// Select a node by its label (ONG name or ISU code/county) — used for deep-links
export function selectNet2ByName(name) {
    if (!net2Data || !name) return;
    const decoded = decodeURIComponent(name);
    const entry = Object.values(net2Data.nodes).find(n =>
        n.label === decoded || n.fullName === decoded);
    if (!entry) return;

    const existing = currentNodes.find(n => n.id === entry.id);
    if (existing) {
        setTimeout(() => selectNode(existing), 100);
    } else {
        // Hidden by the current context filter — show everything then select
        enableAllContexts();
        rebuildGraph();
        setTimeout(() => {
            const n2 = currentNodes.find(n => n.id === entry.id);
            if (n2) selectNode(n2);
        }, 350);
    }
}

function showDetailCard(d) {
    const detail = document.getElementById('partner-detail2');
    const content = document.getElementById('detail-content2');

    // Lists reflect the currently rendered graph (active context filter),
    // and each tag is clickable — same behavior as clicking the node itself.
    const ids = connectedIdSet(d);
    const neighbors = currentNodes.filter(n => n.id !== d.id && ids.has(n.id));
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

        const myIsu = neighbors.filter(n2 => n2.type === 'ISU');
        html += `<div class="detail-domains-label">Județe acoperite (${myIsu.length})</div>`;
        html += `<div class="detail-domains">`;
        myIsu.sort((a, b) => a.data.label.localeCompare(b.data.label)).forEach(isu => {
            html += `<span class="tag-domain tag-clickable" data-node-id="${isu.id}" title="${escapeHtml(isu.data.fullName)}">${escapeHtml(isu.data.label)}</span>`;
        });
        html += `</div>`;
    } else {
        const n = d.data;
        const partners = neighbors.filter(n2 => n2.type === 'ONG');
        html += `<div class="detail-name">ISU ${escapeHtml(n.fullName)}</div>`;
        html += `<div class="detail-type">Inspectorat pentru Situații de Urgență (${escapeHtml(n.label)})</div>`;
        html += `<div class="domain-partner-count">Au colaborat operațional <strong>${partners.length}</strong> ONG-uri afișate în acest județ.</div>`;
        if (partners.length > 0) {
            html += `<div class="detail-domains-label" style="margin-top:12px">ONG-uri colaboratoare</div>`;
            html += `<div class="detail-domains">`;
            partners.sort((a, b) => a.data.label.localeCompare(b.data.label)).forEach(p => {
                html += `<span class="tag-domain tag-clickable" data-node-id="${p.id}">${escapeHtml(p.data.label)}</span>`;
            });
            html += `</div>`;
        }
    }

    content.innerHTML = html;
    detail.classList.remove('hidden');

    content.querySelectorAll('.tag-clickable').forEach(tag => {
        tag.addEventListener('click', () => {
            const node = currentNodes.find(n => n.id === tag.dataset.nodeId);
            if (node) selectNode(node);
        });
    });
}

// ---- CONTROLS (filter bar: search + context dropdown + help) ----

function buildControls() {
    buildContextFilter();
    setupContextDropdown();
    buildNet2Search();
    buildNet2Help();
}

function buildContextFilter() {
    const container = document.getElementById('net2-context-filters');
    if (!container) return;

    // Count ONGs per context (static totals shown next to each option)
    const counts = {};
    for (const n of Object.values(net2Data.nodes)) {
        if (n.type === 'ONG') counts[n.context] = (counts[n.context] || 0) + 1;
    }

    let html = '';
    for (const [key, cfg] of Object.entries(NET2_CONTEXTS)) {
        html += `<label class="filter-checkbox">
            <input type="checkbox" value="${escapeHtml(key)}" checked>
            <span class="filter-dot" style="background:${cfg.color}"></span>
            <span class="filter-label">${escapeHtml(cfg.label)}</span>
            <span class="filter-count">${counts[key] || 0}</span>
        </label>`;
    }
    container.innerHTML = html;

    container.querySelectorAll('input[type="checkbox"]').forEach(cb => {
        cb.addEventListener('change', () => {
            const checked = [...container.querySelectorAll('input[type="checkbox"]:checked')].map(c => c.value);
            if (checked.length === 0) { cb.checked = true; return; } // keep at least one
            activeContexts = new Set(checked);
            updateContextCountLabel();
            deselectNode();
            rebuildGraph();
        });
    });
    updateContextCountLabel();
}

function updateContextCountLabel() {
    const label = document.getElementById('net2-context-count');
    if (!label) return;
    const total = Object.keys(NET2_CONTEXTS).length;
    label.textContent = activeContexts.size < total ? `${activeContexts.size}/${total}` : '';
}

function setupContextDropdown() {
    const btn = document.getElementById('net2-context-btn');
    const panel = document.getElementById('net2-context-panel');
    if (!btn || !panel) return;
    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        panel.classList.toggle('hidden');
    });
    panel.addEventListener('click', (e) => e.stopPropagation());
    document.addEventListener('click', (e) => {
        if (!btn.contains(e.target) && !panel.contains(e.target)) panel.classList.add('hidden');
    });
}

function enableAllContexts() {
    activeContexts = new Set(Object.keys(NET2_CONTEXTS));
    document.querySelectorAll('#net2-context-filters input[type="checkbox"]').forEach(c => c.checked = true);
    updateContextCountLabel();
}

function buildNet2Search() {
    const input = document.getElementById('net2-search');
    const resultsEl = document.getElementById('net2-search-results');
    if (!input || !resultsEl) return;

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
                    // ONG hidden by the current context filter — enable all and retry
                    enableAllContexts();
                    rebuildGraph();
                    setTimeout(() => {
                        const n2 = currentNodes.find(n => n.id === item.dataset.id);
                        if (n2) selectNode(n2);
                    }, 250);
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

// ---- HELP / EXPLANATION CARD ----

function buildNet2Help() {
    const page = document.getElementById('graph-container2');
    if (!page || document.getElementById('net2-help-card')) return;

    const card = document.createElement('div');
    card.id = 'net2-help-card';
    card.className = 'nav-help-card';
    card.innerHTML = `
        <button id="net2-help-close" class="nav-help-close" title="Închide">&times;</button>
        <div class="nav-help-title">Rețea operațională ONG&nbsp;↔&nbsp;ISU</div>
        <div class="nav-help-intro">
            Acest graf arată <strong>colaborările operaționale</strong> dintre organizațiile
            neguvernamentale (ONG) și Inspectoratele Județene pentru Situații de Urgență (ISU)
            în timpul <strong>pandemiei</strong> și al <strong>crizei refugiaților</strong> din Ucraina.
        </div>
        <div class="nav-help-subtitle">Ce vezi</div>
        <div class="nav-help-content">
            <div class="nav-help-item"><span class="legend-diamond" style="display:inline-block;width:9px;height:9px"></span> <strong>Romb roșu</strong> = un județ (ISU)</div>
            <div class="nav-help-item"><span class="legend-dot" style="display:inline-block;width:9px;height:9px;background:#3b82f6"></span> <strong>Cerc</strong> = un ONG, colorat după tip; mărimea = nr. colaborări</div>
            <div class="nav-help-item"><strong>Liniile</strong> leagă fiecare ONG de județele în care a colaborat</div>
        </div>
        <div class="nav-help-subtitle">Cum navighezi</div>
        <div class="nav-help-content">
            <div class="nav-help-item"><strong>Click</strong> pe un județ &ndash; vezi toate ONG-urile care au colaborat acolo</div>
            <div class="nav-help-item"><strong>Click</strong> pe un ONG &ndash; vezi județele și descrierea acțiunii</div>
            <div class="nav-help-item"><strong>Scroll</strong> &ndash; zoom &middot; <strong>Drag</strong> &ndash; mută</div>
            <div class="nav-help-item"><strong>Context</strong> &ndash; filtrează după criză din bara de sus</div>
        </div>
    `;
    page.appendChild(card);

    const btn = document.createElement('button');
    btn.id = 'net2-help-btn';
    btn.className = 'nav-help-btn';
    btn.innerHTML = icons.help({ size: 14 });
    btn.title = 'Cum citești această rețea';
    btn.style.display = 'none';
    const btnContainer = document.getElementById('net2-help-btn-container');
    (btnContainer || page).appendChild(btn);

    if (localStorage.getItem('dsu-net2-help-dismissed')) {
        card.style.display = 'none';
        btn.style.display = '';
    }

    document.getElementById('net2-help-close').addEventListener('click', () => {
        card.style.display = 'none';
        btn.style.display = '';
        localStorage.setItem('dsu-net2-help-dismissed', '1');
    });
    btn.addEventListener('click', () => {
        card.style.display = '';
        btn.style.display = 'none';
    });
}

// ---- LEGEND ----

function buildLegend() {
    const panel = document.getElementById('legend-panel2');
    if (!panel) return;

    const ongNodes = Object.values(net2Data.nodes).filter(n => n.type === 'ONG');
    const present = new Set(ongNodes.map(n => n.tipActor));

    let html = '<div class="legend-section-title">Tip organizație</div>';
    for (const [key, cfg] of Object.entries(ACTOR_TYPES)) {
        if (!present.has(key)) continue;
        html += `<div class="legend-item"><span class="legend-dot" style="background:${cfg.color}"></span><span>${cfg.label}</span></div>`;
    }
    html += '<div class="legend-item"><span class="legend-diamond"></span><span>ISU județean (hub)</span></div>';
    html += '<div class="legend-section-title" style="margin-top:10px">Culoarea muchiei = context</div>';
    for (const [, cfg] of Object.entries(NET2_CONTEXTS)) {
        html += `<div class="legend-item"><span class="legend-line" style="background:${cfg.color}"></span><span>${cfg.label}</span></div>`;
    }
    html += '<div class="legend-note">Mărimea nodului = nr. colaborări</div>';

    panel.innerHTML = html;
}

// ---- ANALYSIS PANEL (network metrics) ----

function buildAnalysisPanel() {
    const panel = document.getElementById('analysis-panel2');
    if (!panel) return;
    const { nodes, edges, stats } = net2Data;

    const ongIds = [], isuIds = [];
    for (const [id, n] of Object.entries(nodes)) {
        (n.type === 'ONG' ? ongIds : isuIds).push(id);
    }
    const ids = [...ongIds, ...isuIds];
    const deg = degreeMap(ids, edges);
    const bc = betweennessCentrality(ids, edges);

    // ONGs that bridge counties (betweenness), with coverage shown as N/34
    const topOng = ongIds
        .map(id => ({ label: nodes[id].label, bc: bc.get(id) || 0, deg: deg.get(id) || 0 }))
        .sort((a, b) => b.bc - a.bc || b.deg - a.deg)
        .slice(0, 5);
    const maxBc = topOng[0]?.bc || 1;

    // Counties with the most NGO collaborators
    const topIsu = isuIds
        .map(id => ({ label: nodes[id].fullName, deg: deg.get(id) || 0 }))
        .sort((a, b) => b.deg - a.deg)
        .slice(0, 3);

    const avgCoverage = ongIds.length
        ? (edges.length / ongIds.length).toLocaleString('ro-RO', { maximumFractionDigits: 1 })
        : '0';
    const lead = topOng[0];

    let html = '<div class="legend-section-title">Analiză de rețea</div>';
    html += `<div class="ap-grid">
        <div class="ap-cell"><div class="ap-cell-value">${stats.ongCount}</div><div class="ap-cell-label">ONG-uri</div></div>
        <div class="ap-cell"><div class="ap-cell-value">${stats.isuCount}</div><div class="ap-cell-label">ISU județene</div></div>
        <div class="ap-cell"><div class="ap-cell-value">${stats.conexiuni.toLocaleString('ro-RO')}</div><div class="ap-cell-label">Conexiuni</div></div>
        <div class="ap-cell"><div class="ap-cell-value">${avgCoverage}</div><div class="ap-cell-label">Județe / ONG</div></div>
    </div>`;

    if (lead) {
        html += `<div class="ap-finding"><strong>${escapeHtml(lead.label)}</strong> este puntea principală a
            rețelei operaționale: a colaborat cu ISU în <strong>${lead.deg} din ${stats.isuCount}</strong> județe,
            legând comunități care altfel nu s-ar intersecta.</div>`;
    }

    html += '<div class="legend-section-title" style="margin-top:12px">Punți între județe · centralitate de intermediere</div>';
    html += '<div class="ap-rank-list">';
    topOng.forEach((o, i) => {
        const pct = Math.max(6, Math.round((o.bc / maxBc) * 100));
        html += `<button class="ap-rank-item" data-label="${escapeHtml(o.label)}" title="${escapeHtml(o.label)}">
            <span class="ap-rank-pos">${i + 1}</span>
            <span class="ap-rank-main">
                <span class="ap-rank-name">${escapeHtml(truncate(o.label, 30))}</span>
                <span class="ap-rank-bar"><span style="width:${pct}%"></span></span>
            </span>
            <span class="ap-rank-badge">${o.deg}/${stats.isuCount} jud.</span>
        </button>`;
    });
    html += '</div>';

    html += '<div class="legend-section-title" style="margin-top:12px">Hub-uri județene · cele mai conectate ISU</div>';
    html += '<div class="ap-rank-list">';
    topIsu.forEach((h, i) => {
        html += `<button class="ap-rank-item" data-label="${escapeHtml(h.label)}" title="ISU ${escapeHtml(h.label)}">
            <span class="ap-rank-pos">${i + 1}</span>
            <span class="ap-rank-main"><span class="ap-rank-name">ISU ${escapeHtml(h.label)}</span></span>
            <span class="ap-rank-badge">${h.deg} ONG</span>
        </button>`;
    });
    html += '</div>';

    html += `<div class="ap-note">Centralitatea de intermediere (algoritmul Brandes) identifică organizațiile
        care fac legătura între județe — actorii critici pentru circulația resurselor și a informației în criză.
        Indicatorii sunt calculați pe rețeaua completă, fără filtre.</div>`;

    panel.innerHTML = html;
    panel.querySelectorAll('.ap-rank-item').forEach(btn => {
        btn.addEventListener('click', () => selectNet2ByName(btn.dataset.label));
    });
}

// ---- TOOLBAR ----

function setupToolbar() {
    document.getElementById('net2-reset-btn')?.addEventListener('click', () => {
        deselectNode();
        zoomReset();
    });

    document.getElementById('net2-export-btn')?.addEventListener('click', () => {
        if (svg) downloadSvg(svg.node(), width, height, 'retea-operationala-isu.svg');
    });
    document.getElementById('net2-export-png-btn')?.addEventListener('click', () => {
        if (svg) downloadPng(svg.node(), width, height, 'retea-operationala-isu.png');
    });

    // Legend / analysis floating panels — one open at a time
    const pairs = [
        { btn: 'legend-toggle2', panel: 'legend-panel2' },
        { btn: 'analysis-toggle2', panel: 'analysis-panel2' }
    ];
    pairs.forEach(({ btn, panel }) => {
        const b = document.getElementById(btn);
        const p = document.getElementById(panel);
        if (!b || !p) return;
        b.addEventListener('click', () => {
            const willOpen = p.classList.contains('hidden');
            pairs.forEach(other => document.getElementById(other.panel)?.classList.add('hidden'));
            if (willOpen) p.classList.remove('hidden');
        });
    });
    // Open the legend by default on desktop
    if (window.innerWidth >= 768) document.getElementById('legend-panel2')?.classList.remove('hidden');

    document.getElementById('close-detail2')?.addEventListener('click', deselectNode);

    document.addEventListener('keydown', (e) => {
        if (!isActive()) return;
        if (e.key === 'Escape') {
            if (selectedNodeId) deselectNode();
            document.getElementById('net2-search-results')?.classList.add('hidden');
            document.getElementById('net2-context-panel')?.classList.add('hidden');
        }
    });
}

// ---- STATS / EMPTY ----

let statsAnimated = false;

function updateStats(ong, isu, colab, conn) {
    if (!statsAnimated) {
        // First render: animate the counters up from zero
        countUp(document.getElementById('n2-stat-ong'), ong);
        countUp(document.getElementById('n2-stat-isu'), isu);
        countUp(document.getElementById('n2-stat-colab'), colab);
        countUp(document.getElementById('n2-stat-conn'), conn);
        statsAnimated = true;
        return;
    }
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
