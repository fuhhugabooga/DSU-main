/* =========================================
   NETWORK METRICS — degree & betweenness centrality
   Computed client-side on the full (unfiltered) graphs and surfaced in
   the "Analiză de rețea" panels of both network views.
   ========================================= */

// Build an undirected adjacency map. Edges whose endpoints are not in `ids`
// are ignored (e.g. FONSS member edges excluded from the partner analysis).
function buildAdjacency(ids, edges) {
    const adj = new Map(ids.map(id => [id, []]));
    for (const e of edges) {
        if (adj.has(e.source) && adj.has(e.target)) {
            adj.get(e.source).push(e.target);
            adj.get(e.target).push(e.source);
        }
    }
    return adj;
}

// Betweenness centrality via Brandes' algorithm (unweighted, undirected).
// O(V·E) — instant at this scale (≤ ~300 nodes, ~600 edges).
export function betweennessCentrality(ids, edges) {
    const adj = buildAdjacency(ids, edges);
    const bc = new Map(ids.map(id => [id, 0]));

    for (const s of ids) {
        const stack = [];
        const pred = new Map(ids.map(id => [id, []]));
        const sigma = new Map(ids.map(id => [id, 0]));
        const dist = new Map(ids.map(id => [id, -1]));
        sigma.set(s, 1);
        dist.set(s, 0);

        const queue = [s];
        let head = 0;
        while (head < queue.length) {
            const v = queue[head++];
            stack.push(v);
            for (const w of adj.get(v)) {
                if (dist.get(w) < 0) {
                    dist.set(w, dist.get(v) + 1);
                    queue.push(w);
                }
                if (dist.get(w) === dist.get(v) + 1) {
                    sigma.set(w, sigma.get(w) + sigma.get(v));
                    pred.get(w).push(v);
                }
            }
        }

        const delta = new Map(ids.map(id => [id, 0]));
        while (stack.length) {
            const w = stack.pop();
            for (const v of pred.get(w)) {
                delta.set(v, delta.get(v) + (sigma.get(v) / sigma.get(w)) * (1 + delta.get(w)));
            }
            if (w !== s) bc.set(w, bc.get(w) + delta.get(w));
        }
    }

    // Undirected graph: every pair was counted twice
    for (const [id, v] of bc) bc.set(id, v / 2);
    return bc;
}

export function degreeMap(ids, edges) {
    const adj = buildAdjacency(ids, edges);
    return new Map(ids.map(id => [id, adj.get(id).length]));
}

// Density of a bipartite graph = edges / (|A| · |B|)
export function bipartiteDensity(countA, countB, edgeCount) {
    const max = countA * countB;
    return max > 0 ? edgeCount / max : 0;
}

export function formatPercent(x) {
    return (x * 100).toLocaleString('ro-RO', { maximumFractionDigits: 1 }) + '%';
}
