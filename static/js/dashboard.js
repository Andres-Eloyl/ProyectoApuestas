document.addEventListener("DOMContentLoaded", () => {

    // 1. Fetch Precision Metrics
    fetch('/api/metricas_globales')
        .then(res => res.json())
        .then(data => {
            const elPrecision = document.getElementById('ui-precision');
            const elAciertos = document.getElementById('ui-aciertos');
            const elFallos = document.getElementById('ui-fallos');
            const elEficiencia = document.getElementById('ui-eficiencia-ligas');
            const elRoi = document.getElementById('ui-roi');
            const elWr = document.getElementById('ui-wr');
            const elAcc = document.getElementById('ui-acc');

            if (elPrecision) elPrecision.textContent = `${data.Precision_Global.toFixed(1)}%`;
            if (elAciertos) elAciertos.textContent = `+${data.Aciertos}`;
            if (elFallos) elFallos.textContent = `-${data.Fallos}`;

            // Stats en header superior
            if (elRoi) elRoi.textContent = `+${(data.Precision_Global / 10).toFixed(1)}% ROI`; // Estimado
            if (elWr) elWr.textContent = `${data.Precision_Global.toFixed(1)}% WR`;
            if (elAcc) elAcc.textContent = `${data.Precision_Global.toFixed(0)}% ACC`;

            if (elEficiencia && data.Desglose_Ligas) {
                elEficiencia.innerHTML = '';
                const ligasObj = data.Desglose_Ligas;

                // Colors map
                const colorMap = { "Premier League": "emerald-500", "La Liga": "primary", "Serie A": "orange-500", "Bundesliga": "yellow-500", "Ligue 1": "blue-400" };
                const shortMap = { "Premier League": "PL", "La Liga": "LL", "Serie A": "SA", "Bundesliga": "BL", "Ligue 1": "L1", "Champions League": "UCL" };

                for (const liga in ligasObj) {
                    const stats = ligasObj[liga];
                    const color = colorMap[liga] || "primary";
                    const shortName = shortMap[liga] || liga.substring(0, 2).toUpperCase();

                    elEficiencia.innerHTML += `
                    <div class="flex items-center gap-3">
                        <span class="text-[10px] font-black text-white w-6">${shortName}</span>
                        <div class="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
                            <div class="h-full bg-${color}" style="width: ${stats.precision}%"></div>
                        </div>
                        <span class="text-[10px] font-bold text-${color}">${stats.precision.toFixed(0)}%</span>
                    </div>`;
                }
            }

            // Draw Precision Chart
            const ctx = document.getElementById('precisionChart');
            if (ctx && data.Desglose_Ligas) {
                Chart.defaults.color = '#94a3b8'; // text-slate-400
                Chart.defaults.font.family = "'Inter', sans-serif";

                const ligasObj = data.Desglose_Ligas;
                const ligas = Object.keys(ligasObj);
                const winRates = ligas.map(l => ligasObj[l].precision);
                const bgColors = winRates.map(w => w >= 50 ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)'); // emerald-500 or red-500
                const borderColors = winRates.map(w => w >= 50 ? '#10b981' : '#ef4444');

                new Chart(ctx.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: ligas,
                        datasets: [{
                            label: 'Precisión IA (%)',
                            data: winRates,
                            backgroundColor: bgColors,
                            borderColor: borderColors,
                            borderWidth: 2,
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { grid: { display: false, drawBorder: false } },
                            y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255,255,255,0.05)', drawBorder: false } }
                        }
                    }
                });
            }
        });

    // 2. Fetch Real-time Predictions & Terminal
    const tbodyTerminal = document.getElementById('ui-terminal-body');
    const alertasValors = document.getElementById('ui-alertas');
    const marquee = document.getElementById('ui-marquee');

    if (tbodyTerminal) {
        tbodyTerminal.innerHTML = `<tr><td colspan="7" class="text-center p-4">Iniciando oráculo neuronal neuronal...</td></tr>`;
    }

    fetch('/api/sync_predicciones')
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                if (tbodyTerminal) tbodyTerminal.innerHTML = `<tr><td colspan="7" class="text-center text-red-500 p-4">Error: ${data.error}</td></tr>`;
                return;
            }
            renderTerminalAndAlertas(data);
        })
        .catch(err => {
            if (tbodyTerminal) tbodyTerminal.innerHTML = `<tr><td colspan="7" class="text-center text-red-500 p-4">Falla de conexión con el backend.</td></tr>`;
        });

    function renderTerminalAndAlertas(predictions) {
        if (tbodyTerminal) tbodyTerminal.innerHTML = '';
        if (alertasValors) alertasValors.innerHTML = '';

        let marqueeText = "";

        // Ordenamos las alertas de valor (solo EV > 1.0) por EV
        const valuePicks = [...predictions].filter(p => parseFloat(p.EV) > 1.0).sort((a, b) => b.EV - a.EV);

        // Render Alertas de Valor (Top 4)
        valuePicks.slice(0, 4).forEach((p, index) => {
            const colors = ['primary', 'emerald-500', 'orange-500', 'slate-400'];
            const color = colors[index % colors.length];
            const ev = parseFloat(p.EV);
            const valueStr = ev > 1.0 ? `+${(ev - 1.0).toFixed(2)}v` : '0.00v';

            alertasValors.innerHTML += `
            <div class="p-2 border-l-2 border-${color} bg-slate-900/40 flex items-center justify-between group cursor-pointer hover:bg-slate-900">
                <div>
                    <p class="text-[9px] text-slate-500 font-bold uppercase">${p.HomeTeam} vs ${p.AwayTeam}</p>
                    <p class="text-[11px] font-black text-white">${p.Recomendacion !== 'No Bet' ? p.Recomendacion : 'Revisión Manual'}</p>
                </div>
                <div class="text-right">
                    <p class="text-[10px] font-black text-${color}">${valueStr}</p>
                    <p class="text-[9px] text-slate-500 font-bold">@${p.Cuota}</p>
                </div>
            </div>`;
        });

        // Render Terminal Body
        predictions.forEach(p => {
            const isInvest = p.Recomendacion !== 'No Bet';
            const colorClass = isInvest ? 'emerald-500' : 'slate-500';
            const bgClass = isInvest ? 'emerald-500/10' : 'slate-500/10';
            const ev = parseFloat(p.EV);
            const valueStr = ev > 1.0 ? `+${((ev - 1.0) * 100).toFixed(1)}%` : '0.0%';

            // Marquee Text Building
            marqueeText += ` • ${p.HomeTeam.toUpperCase()} vs ${p.AwayTeam.toUpperCase()} (xG: ${p.Proj_Goles_L} - ${p.Proj_Goles_V})`;

            tbodyTerminal.innerHTML += `
            <tr class="border-b border-slate-800/50 hover:bg-slate-900/30 transition-colors">
                <td class="p-4">
                    <span class="text-white font-bold block">${p.HomeTeam} vs ${p.AwayTeam}</span> 
                    <span class="text-[9px] text-slate-600 font-black uppercase tracking-widest">${p.Recomendacion !== 'No Bet' ? 'EV+ Detectado' : 'Sin Valor'}</span>
                </td>
                <td class="p-4"><span class="px-2 py-0.5 bg-${bgClass} text-${colorClass} rounded font-black">${(p.Probabilidad * 10).toFixed(1)}</span></td>
                <td class="p-4">${p.Proj_Goles_L} / ${p.Proj_Goles_V}</td>
                <td class="p-4">
                    <div class="flex gap-0.5">
                        <div class="h-4 w-1 bg-${colorClass}"></div>
                        <div class="h-4 w-1 bg-${colorClass}"></div>
                        <div class="h-4 w-1 bg-${colorClass}/${isInvest ? '50' : '100'}"></div>
                        <div class="h-4 w-1 bg-${colorClass}/${isInvest ? '30' : '100'}"></div>
                    </div>
                </td>
                <td class="p-4">${p.Cuota}</td>
                <td class="p-4 text-${colorClass} font-bold">${valueStr}</td>
                <td class="p-4">
                    <div class="h-1 w-12 bg-slate-800 rounded-full overflow-hidden">
                        <div class="h-full bg-primary" style="width: ${(p.Probabilidad * 100).toFixed(0)}%"></div>
                    </div>
                </td>
            </tr>`;
        });

        if (marquee) {
            marquee.textContent = marqueeText + " " + marqueeText; // Duplicate for smooth looping
        }
    }

    // 3. Fetch Insights para Sugerencia del Sistema
    fetch('/api/insights')
        .then(res => res.json())
        .then(data => {
            const elSugerencia = document.getElementById('ui-sugerencia');
            if (elSugerencia && data.length > 0) {
                // Use the first insight
                elSugerencia.textContent = `"${data[0].mensaje}"`;
            } else if (elSugerencia) {
                elSugerencia.textContent = "Sin anomalías detectadas en mercados primarios de la sesión.";
            }
        });

    // 4. Fetch Historial Auditoria
    fetch('/api/historial_evaluado')
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('ui-auditoria-body');
            if (!tbody) return;
            tbody.innerHTML = '';
            if (!data || data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" class="p-4 text-center">Sin datos recientes</td></tr>';
                return;
            }

            // Limit to last 5
            const recent = data.slice(-5).reverse();
            recent.forEach(p => {
                const isHit = p.Acierto === "✅";
                const color = isHit ? 'emerald-500' : 'red-500';
                tbody.innerHTML += `
                <tr class="border-b border-slate-800/50 hover:bg-slate-900/30 transition-colors">
                    <td class="p-4">${p.Fecha}</td>
                    <td class="p-4"><strong class="text-white">${p.Partido}</strong></td>
                    <td class="p-4 text-primary font-bold">${p.Prediccion_IA}</td>
                    <td class="p-4 text-${color} font-black">${p.Resultado_Real || '-'} ${p.Acierto}</td>
                </tr>`;
            });
        });

});
