from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402


NAVY = "#173A5E"
INK = "#17212B"
MUTED = "#66717C"
GRID = "#E2E8ED"
TEAL = "#1C8C86"
ORANGE = "#D4763B"
PURPLE = "#7652A8"
SOFT_TEAL = "#E7F4F1"
SOFT_ORANGE = "#FFF0E5"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def style_axis(axis: plt.Axes) -> None:
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color(GRID)
    axis.grid(axis="y", color=GRID, linewidth=0.8)
    axis.tick_params(colors=MUTED, labelsize=8)
    axis.set_axisbelow(True)


def metric_box(fig: plt.Figure, x: float, y: float, width: float, title: str, value: str) -> None:
    box = FancyBboxPatch(
        (x, y), width, 0.075,
        boxstyle="round,pad=0.008,rounding_size=0.012",
        transform=fig.transFigure,
        facecolor="#FFFFFF",
        edgecolor=GRID,
        linewidth=1.0,
    )
    fig.patches.append(box)
    fig.text(x + 0.014, y + 0.052, title.upper(), fontsize=7, color=MUTED, weight="bold")
    fig.text(x + 0.014, y + 0.019, value, fontsize=9.4, color=INK, weight="bold")


def linkedin_overview(scenario: dict, destination: Path) -> None:
    rows = scenario["rows"]
    metrics = scenario["metrics"]
    hours = [row["hour"] for row in rows]
    fig = plt.figure(figsize=(7.2, 9.0), dpi=150, facecolor="#F4F6F8")
    header = FancyBboxPatch(
        (0, 0.865), 1, 0.135, boxstyle="square,pad=0",
        transform=fig.transFigure, facecolor=NAVY, edgecolor=NAVY,
    )
    fig.patches.append(header)
    fig.text(0.06, 0.958, "OPEN-SOURCE · GRID-AWARE · ADVISORY FIRST", fontsize=7.5, color="#A9C7DE", weight="bold")
    fig.text(0.06, 0.915, "Can a data center become a better grid citizen?", fontsize=16.5, color="white", weight="bold")
    fig.text(0.06, 0.883, "CoolRide-PQ · synthetic 50 MW IT / 65 MW facility reference day", fontsize=9, color="#D5E2EB")

    metric_box(fig, 0.055, 0.772, 0.205, "Net energy", f"{metrics['net_energy_change_mwh']:.1f} MWh  |  {metrics['net_energy_change_percent']:.1f}%")
    metric_box(fig, 0.282, 0.772, 0.205, "PCC peak", f"−{metrics['peak_reduction_mw']:.1f} MW  |  −{metrics['peak_reduction_percent']:.1f}%")
    metric_box(fig, 0.509, 0.772, 0.205, "Minimum voltage", f"{metrics['minimum_voltage_baseline_pu']:.3f} → {metrics['minimum_voltage_controlled_pu']:.3f} p.u.")
    metric_box(fig, 0.736, 0.772, 0.205, "Maximum THDv", f"{metrics['maximum_thdv_baseline_percent']:.1f} → {metrics['maximum_thdv_controlled_percent']:.1f}%")

    power_axis = fig.add_axes((0.075, 0.535, 0.85, 0.18), facecolor="white")
    power_axis.plot(hours, [r["pcc_power_baseline_mw"] for r in rows], color=ORANGE, lw=1.7, label="Uncoordinated baseline")
    power_axis.plot(hours, [r["pcc_power_controlled_mw"] for r in rows], color=TEAL, lw=2.0, label="CoolRide-PQ")
    power_axis.axvspan(17.75, 18.55, color=SOFT_ORANGE, zorder=0)
    power_axis.set_title("PCC active-power profile", loc="left", fontsize=10, color=INK, weight="bold")
    power_axis.set_ylabel("MW", fontsize=8, color=MUTED)
    power_axis.set_xlim(0, 24)
    power_axis.set_xticks([0, 6, 12, 18, 24], ["00:00", "06:00", "12:00", "18:00", "24:00"])
    power_axis.legend(loc="upper left", frameon=False, fontsize=8, ncol=2)
    style_axis(power_axis)

    voltage_axis = fig.add_axes((0.075, 0.315, 0.40, 0.16), facecolor="white")
    voltage_axis.axhspan(0.95, 1.05, color=SOFT_TEAL, zorder=0)
    voltage_axis.plot(hours, [r["pcc_voltage_baseline_pu"] for r in rows], color=ORANGE, lw=1.4)
    voltage_axis.plot(hours, [r["pcc_voltage_controlled_pu"] for r in rows], color=TEAL, lw=1.8)
    voltage_axis.set_title("PCC voltage during the 18:03 disturbance", loc="left", fontsize=9, color=INK, weight="bold")
    voltage_axis.set_xlim(17.4, 19.0)
    voltage_axis.set_ylim(0.84, 1.025)
    voltage_axis.set_ylabel("p.u.", fontsize=8, color=MUTED)
    style_axis(voltage_axis)

    action_axis = fig.add_axes((0.535, 0.315, 0.39, 0.16), facecolor="white")
    action_axis.plot(hours, [r["bess_active_power_mw"] for r in rows], color=PURPLE, lw=1.6, label="BESS P")
    action_axis.plot(hours, [r["bess_reactive_power_mvar"] for r in rows], color=NAVY, lw=1.4, ls="--", label="BESS Q")
    action_axis.plot(hours, [r["thermal_power_mw"] for r in rows], color=TEAL, lw=1.3, ls="--", label="Thermal")
    action_axis.plot(hours, [r["it_defer_mw"] for r in rows], color=ORANGE, lw=1.2, ls=":", label="IT shift")
    action_axis.axhline(0, color=GRID, lw=0.8)
    action_axis.set_title("Bounded supervisory actions", loc="left", fontsize=9, color=INK, weight="bold")
    action_axis.set_xlim(0, 24)
    action_axis.set_ylabel("MW / MVAr", fontsize=8, color=MUTED)
    action_axis.legend(loc="upper left", frameon=False, fontsize=6.8, ncol=2)
    style_axis(action_axis)

    fig.text(0.06, 0.243, "THE ENTERPRISE PROPOSITION", fontsize=8, color=MUTED, weight="bold")
    fig.text(0.06, 0.210, "One auditable layer connects facility efficiency, grid support and model evidence.", fontsize=9.8, color=INK, weight="bold")
    fig.text(0.06, 0.168, "C++20 safety core", fontsize=7.5, color=NAVY, weight="bold")
    fig.text(0.285, 0.168, "Python digital twin", fontsize=7.5, color=NAVY, weight="bold")
    fig.text(0.555, 0.168, "TypeScript console", fontsize=7.5, color=NAVY, weight="bold")
    fig.text(0.815, 0.168, "Bash + containers", fontsize=7.5, color=NAVY, weight="bold")
    fig.text(0.06, 0.125, "Fail-closed bounds", fontsize=6.8, color=MUTED)
    fig.text(0.285, 0.125, "Sizing + control + evidence", fontsize=6.8, color=MUTED)
    fig.text(0.555, 0.125, "Linked engineering views", fontsize=6.8, color=MUTED)
    fig.text(0.815, 0.125, "Repeatable workflows", fontsize=6.8, color=MUTED)

    fig.text(0.06, 0.066, "Simulation—not a performance guarantee. OEM protection, UPS logic and utility authority remain in control.", fontsize=7.5, color=MUTED)
    fig.text(0.06, 0.038, "COOLRIDE-PQ  /  APACHE-2.0  /  INVITATION FOR VALIDATION DATA, HIL BENCHMARKS & ADAPTERS", fontsize=7, color=NAVY, weight="bold")
    fig.savefig(destination / "coolride-pq-linkedin-overview.png", facecolor=fig.get_facecolor())
    plt.close(fig)


def technical_response(scenario: dict, destination: Path) -> None:
    rows = scenario["rows"]
    hours = [row["hour"] for row in rows]
    fig, axes = plt.subplots(4, 1, figsize=(12, 8), dpi=160, sharex=True, facecolor="white")
    fig.suptitle("CoolRide-PQ · 50 MW IT reference day · advisory simulation", x=0.08, ha="left", fontsize=16, color=INK, weight="bold")
    axes[0].plot(hours, [r["pcc_power_baseline_mw"] for r in rows], color=ORANGE, lw=1.7, label="Baseline")
    axes[0].plot(hours, [r["pcc_power_controlled_mw"] for r in rows], color=TEAL, lw=2.0, label="CoolRide-PQ")
    axes[0].set_ylabel("PCC MW")
    axes[0].legend(frameon=False, ncol=2, loc="upper left")
    axes[1].axhspan(.95, 1.05, color=SOFT_TEAL)
    axes[1].plot(hours, [r["pcc_voltage_baseline_pu"] for r in rows], color=ORANGE, lw=1.5)
    axes[1].plot(hours, [r["pcc_voltage_controlled_pu"] for r in rows], color=TEAL, lw=1.8)
    axes[1].set_ylabel("Voltage p.u.")
    axes[2].axhline(5, color=MUTED, lw=1, ls="--", label="design threshold")
    axes[2].plot(hours, [r["thdv_baseline_percent"] for r in rows], color=ORANGE, lw=1.5)
    axes[2].plot(hours, [r["thdv_controlled_percent"] for r in rows], color=TEAL, lw=1.8)
    axes[2].set_ylabel("THDv %")
    axes[3].plot(hours, [r["bess_active_power_mw"] for r in rows], color=PURPLE, lw=1.6, label="BESS P")
    axes[3].plot(hours, [r["bess_reactive_power_mvar"] for r in rows], color=NAVY, lw=1.4, ls="--", label="BESS Q")
    axes[3].plot(hours, [r["thermal_power_mw"] for r in rows], color=TEAL, lw=1.3, ls="--", label="thermal")
    axes[3].plot(hours, [r["it_defer_mw"] for r in rows], color=ORANGE, lw=1.2, ls=":", label="IT shift")
    axes[3].set_ylabel("MW / MVAr")
    axes[3].set_xlabel("Hour")
    axes[3].legend(frameon=False, ncol=4, loc="upper left")
    for axis in axes:
        axis.axvspan(17.75, 18.55, color=SOFT_ORANGE, zorder=0)
        axis.set_xlim(0, 24)
        style_axis(axis)
    fig.text(.08, .015, "Synthetic engineering scenario. Limits are project assumptions, not interconnection compliance results.", fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0.05, 0.04, 0.98, 0.95))
    fig.savefig(destination / "coolride-pq-technical-response.png", bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: render_graphics.py SCENARIO_JSON OUTPUT_DIRECTORY")
    scenario = load(Path(sys.argv[1]))
    destination = Path(sys.argv[2])
    destination.mkdir(parents=True, exist_ok=True)
    linkedin_overview(scenario, destination)
    technical_response(scenario, destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
