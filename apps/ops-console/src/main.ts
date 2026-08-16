type Metrics = {
  baseline_energy_mwh: number;
  controlled_energy_mwh: number;
  net_energy_change_mwh: number;
  net_energy_change_percent: number;
  baseline_peak_mw: number;
  controlled_peak_mw: number;
  peak_reduction_mw: number;
  peak_reduction_percent: number;
  minimum_voltage_baseline_pu: number;
  minimum_voltage_controlled_pu: number;
  maximum_thdv_baseline_percent: number;
  maximum_thdv_controlled_percent: number;
};

type ScenarioRow = {
  hour: number;
  pcc_power_baseline_mw: number;
  pcc_power_controlled_mw: number;
  pcc_voltage_baseline_pu: number;
  pcc_voltage_controlled_pu: number;
  thdv_baseline_percent: number;
  thdv_controlled_percent: number;
  bess_active_power_mw: number;
  bess_reactive_power_mvar: number;
  thermal_power_mw: number;
  it_defer_mw: number;
  mode: string;
};

type Scenario = { metrics: Metrics; rows: ScenarioRow[] };
type Sizing = Record<string, string | number | string[]>;

const svg = document.querySelector<SVGSVGElement>("#scenario-chart")!;
const shell = document.querySelector<HTMLElement>("#chart-shell")!;
const tooltip = document.querySelector<HTMLElement>("#chart-tooltip")!;
let scenario: Scenario | null = null;

const NS = "http://www.w3.org/2000/svg";
function node(name: string, attributes: Record<string, string | number>, content?: string): SVGElement {
  const element = document.createElementNS(NS, name);
  Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, String(value)));
  if (content !== undefined) element.textContent = content;
  return element;
}

function setText(id: string, value: string): void {
  const element = document.querySelector<HTMLElement>(`#${id}`);
  if (element) element.textContent = value;
}

function renderMetrics(metrics: Metrics): void {
  setText("metric-energy", `${metrics.net_energy_change_mwh.toFixed(1)} MWh (${metrics.net_energy_change_percent.toFixed(1)}%)`);
  setText("metric-energy-detail", `${metrics.baseline_energy_mwh.toFixed(0)} → ${metrics.controlled_energy_mwh.toFixed(0)} MWh/day`);
  setText("metric-peak", `${metrics.peak_reduction_mw.toFixed(1)} MW (${metrics.peak_reduction_percent.toFixed(1)}%)`);
  setText("metric-peak-detail", `${metrics.baseline_peak_mw.toFixed(1)} → ${metrics.controlled_peak_mw.toFixed(1)} MW`);
  setText("metric-voltage", `${metrics.minimum_voltage_baseline_pu.toFixed(3)} → ${metrics.minimum_voltage_controlled_pu.toFixed(3)} p.u.`);
  setText("metric-thd", `${metrics.maximum_thdv_baseline_percent.toFixed(1)} → ${metrics.maximum_thdv_controlled_percent.toFixed(1)}%`);
}

function renderSizing(sizing: Sizing): void {
  const grid = document.querySelector<HTMLElement>("#sizing-grid")!;
  const entries: [string, string][] = [
    ["Facility capacity", `${Number(sizing.facility_capacity_mw).toFixed(1)} MW`],
    ["Racks", `${sizing.rack_count} × 80 kW`],
    ["Heat rejection", `${Number(sizing.heat_rejection_capacity_mw_thermal).toFixed(1)} MWth`],
    ["Liquid-cooled IT", `${Number(sizing.liquid_cooled_it_mw).toFixed(1)} MW`],
    ["Installed UPS", `${sizing.installed_ups_modules} modules / ${Number(sizing.installed_ups_capacity_mva).toFixed(0)} MVA`],
    ["Standby generation", `${Number(sizing.standby_generation_capacity_mw).toFixed(1)} MW`],
    ["UPS ride-through", `${Number(sizing.ups_ride_through_energy_mwh).toFixed(2)} MWh`],
    ["Grid-flexibility BESS", `10 MW / 30 MWh`],
  ];
  grid.replaceChildren(...entries.map(([label, value]) => {
    const wrapper = document.createElement("div");
    const term = document.createElement("dt");
    const detail = document.createElement("dd");
    term.textContent = label;
    detail.textContent = value;
    wrapper.append(term, detail);
    return wrapper;
  }));
}

function path(rows: ScenarioRow[], x: (v: number) => number, y: (v: number) => number, key: keyof ScenarioRow): string {
  return rows.map((row, index) => `${index ? "L" : "M"}${x(row.hour).toFixed(2)},${y(Number(row[key])).toFixed(2)}`).join(" ");
}

function drawChart(): void {
  if (!scenario) return;
  const rows = scenario.rows;
  const width = Math.max(300, Math.floor(shell.getBoundingClientRect().width));
  const height = width < 520 ? 760 : 710;
  svg.setAttribute("width", String(width));
  svg.setAttribute("height", String(height));
  svg.style.height = `${height}px`;
  svg.replaceChildren();
  const left = width < 520 ? 45 : 58;
  const right = width - 12;
  const startTop = 28;
  const gap = 38;
  const panelHeight = (height - startTop - 48 - 3 * gap) / 4;
  const panels = Array.from({length: 4}, (_, index) => {
    const top = startTop + index * (panelHeight + gap);
    return {top, bottom: top + panelHeight};
  });
  const x = (hour: number) => left + hour / 24 * (right - left);
  const domains: [number, number][] = [[45, 69], [0.84, 1.06], [1.5, 6.5], [-11, 11]];
  const y = domains.map((domain, index) => (value: number) => panels[index].bottom - (value - domain[0]) / (domain[1] - domain[0]) * panelHeight);
  const titles = [["PCC active power", "MW"], ["PCC voltage magnitude", "p.u. RMS"], ["PCC voltage distortion", "THDv %"], ["Controller response", "MW / MVAr"]];
  const ticks = [[45,55,65], [.85,.95,1.05], [2,4,6], [-10,0,10]];

  panels.forEach((panel, panelIndex) => {
    svg.append(node("text", {x:left, y:panel.top-9, class:"chart-label"}, titles[panelIndex][0]));
    svg.append(node("text", {x:right, y:panel.top-9, class:"chart-unit", "text-anchor":"end"}, titles[panelIndex][1]));
    if (panelIndex === 1) svg.append(node("rect", {x:left, y:y[1](1.05), width:right-left, height:y[1](.95)-y[1](1.05), class:"chart-band"}));
    svg.append(node("rect", {x:x(17.75), y:panel.top, width:x(18.55)-x(17.75), height:panelHeight, class:"chart-event"}));
    ticks[panelIndex].forEach(value => {
      svg.append(node("line", {x1:left, y1:y[panelIndex](value), x2:right, y2:y[panelIndex](value), class:"chart-grid"}));
      svg.append(node("text", {x:left-7, y:y[panelIndex](value)+4, class:"chart-tick", "text-anchor":"end"}, panelIndex === 1 ? value.toFixed(2) : String(value)));
    });
    [0,6,12,18,24].forEach(hour => {
      svg.append(node("line", {x1:x(hour), y1:panel.top, x2:x(hour), y2:panel.bottom, class:"chart-grid"}));
      if (panelIndex === 3) svg.append(node("text", {x:x(hour), y:panel.bottom+20, class:"chart-tick", "text-anchor":hour === 0 ? "start" : hour === 24 ? "end" : "middle"}, `${String(hour).padStart(2,"0")}:00`));
    });
    svg.append(node("rect", {x:left, y:panel.top, width:right-left, height:panelHeight, class:"chart-frame", rx:4}));
  });
  svg.append(node("line", {x1:left, y1:y[2](5), x2:right, y2:y[2](5), class:"chart-threshold"}));
  svg.append(node("path", {d:path(rows,x,y[0],"pcc_power_baseline_mw"), class:"chart-baseline"}));
  svg.append(node("path", {d:path(rows,x,y[0],"pcc_power_controlled_mw"), class:"chart-controlled"}));
  svg.append(node("path", {d:path(rows,x,y[1],"pcc_voltage_baseline_pu"), class:"chart-baseline"}));
  svg.append(node("path", {d:path(rows,x,y[1],"pcc_voltage_controlled_pu"), class:"chart-controlled"}));
  svg.append(node("path", {d:path(rows,x,y[2],"thdv_baseline_percent"), class:"chart-baseline"}));
  svg.append(node("path", {d:path(rows,x,y[2],"thdv_controlled_percent"), class:"chart-controlled"}));
  svg.append(node("path", {d:path(rows,x,y[3],"bess_active_power_mw"), class:"chart-bess"}));
  svg.append(node("path", {d:path(rows,x,y[3],"bess_reactive_power_mvar"), class:"chart-q"}));
  svg.append(node("path", {d:path(rows,x,y[3],"thermal_power_mw"), class:"chart-thermal"}));
  svg.append(node("path", {d:path(rows,x,y[3],"it_defer_mw"), class:"chart-it"}));

  const crosshair = node("line", {y1:panels[0].top, y2:panels[3].bottom, class:"chart-crosshair", visibility:"hidden"});
  const hit = node("rect", {x:left, y:panels[0].top, width:right-left, height:panels[3].bottom-panels[0].top, fill:"transparent", style:"cursor:crosshair"});
  svg.append(crosshair, hit);
  hit.addEventListener("pointermove", event => {
    const rect = svg.getBoundingClientRect();
    const px = event.clientX - rect.left;
    const hour = Math.max(0, Math.min(24, (px-left)/(right-left)*24));
    const index = Math.max(0, Math.min(rows.length-1, Math.round(hour*12)));
    const row = rows[index];
    const xx = x(row.hour);
    crosshair.setAttribute("x1", String(xx));
    crosshair.setAttribute("x2", String(xx));
    crosshair.setAttribute("visibility", "visible");
    tooltip.hidden = false;
    tooltip.innerHTML = `<strong>${String(Math.floor(row.hour)).padStart(2,"0")}:${String(Math.round((row.hour%1)*60)).padStart(2,"0")} · ${row.mode.replaceAll("_"," ")}</strong><div class="tooltip-grid"><span>Power</span><span>${row.pcc_power_baseline_mw.toFixed(1)} → ${row.pcc_power_controlled_mw.toFixed(1)} MW</span><span>Voltage</span><span>${row.pcc_voltage_baseline_pu.toFixed(3)} → ${row.pcc_voltage_controlled_pu.toFixed(3)} p.u.</span><span>THDv</span><span>${row.thdv_baseline_percent.toFixed(1)} → ${row.thdv_controlled_percent.toFixed(1)}%</span><span>BESS P</span><span>${row.bess_active_power_mw.toFixed(1)} MW</span><span>BESS Q</span><span>${row.bess_reactive_power_mvar.toFixed(1)} MVAr</span><span>Thermal</span><span>${row.thermal_power_mw.toFixed(1)} MW</span><span>IT shift</span><span>${row.it_defer_mw.toFixed(1)} MW</span></div>`;
    const tipWidth = 250;
    tooltip.style.left = `${Math.max(4, Math.min(width-tipWidth-4, xx+12))}px`;
    tooltip.style.top = `${Math.max(4, Math.min(height-235, event.clientY-shell.getBoundingClientRect().top+10))}px`;
  });
  hit.addEventListener("pointerleave", () => { crosshair.setAttribute("visibility", "hidden"); tooltip.hidden = true; });
}

function renderModes(rows: ScenarioRow[]): void {
  const track = document.querySelector<HTMLElement>("#mode-track")!;
  const segments: {mode: string; count: number}[] = [];
  rows.forEach(row => {
    const prior = segments.at(-1);
    if (prior && prior.mode === row.mode) prior.count += 1;
    else segments.push({mode: row.mode, count: 1});
  });
  track.replaceChildren(...segments.map(segment => {
    const element = document.createElement("span");
    element.className = `mode-segment mode-${segment.mode}`;
    element.style.flex = String(segment.count);
    element.setAttribute("aria-label", `${segment.mode}, ${segment.count*5} minutes`);
    return element;
  }));
}

async function bootstrap(): Promise<void> {
  try {
    const [scenarioResponse, sizingResponse] = await Promise.all([fetch("/api/scenario"), fetch("/api/site/sizing")]);
    if (!scenarioResponse.ok || !sizingResponse.ok) throw new Error("API request failed");
    scenario = await scenarioResponse.json() as Scenario;
    const sizing = await sizingResponse.json() as Sizing;
    renderMetrics(scenario.metrics);
    renderSizing(sizing);
    renderModes(scenario.rows);
    drawChart();
    new ResizeObserver(drawChart).observe(shell);
  } catch (error) {
    document.querySelector("main")!.innerHTML = `<section class="panel"><h2>Console unavailable</h2><p class="disclaimer">Start the local service with ./scripts/run_demo.sh. ${String(error)}</p></section>`;
  }
}

void bootstrap();
