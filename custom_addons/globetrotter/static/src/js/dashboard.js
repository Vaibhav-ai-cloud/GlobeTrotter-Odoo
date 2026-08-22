import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class GlobeTrotterDashboard extends Component {
    static template = "globetrotter.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            error: false,
            metrics: {
                totalTrips: 0,
                draftTrips: 0,
                plannedTrips: 0,
                completedTrips: 0,
                cancelledTrips: 0,
                totalCities: 0,
                totalStops: 0,
                totalDays: 0,
            },
            recentTrips: [],
        });

        onWillStart(() => this.loadDashboard());
    }

    async loadDashboard() {
        try {
            const tripModel = "globetrotter.trip";
            const stopModel = "globetrotter.trip.stop";
            const [totalTrips, draftTrips, plannedTrips, completedTrips, cancelledTrips,
                totalCities, totalStops, stopDurations, recentTrips] = await Promise.all([
                this.orm.searchCount(tripModel, []),
                this.orm.searchCount(tripModel, [["state", "=", "draft"]]),
                this.orm.searchCount(tripModel, [["state", "=", "planned"]]),
                this.orm.searchCount(tripModel, [["state", "=", "completed"]]),
                this.orm.searchCount(tripModel, [["state", "=", "cancelled"]]),
                this.orm.searchCount("globetrotter.city", []),
                this.orm.searchCount(stopModel, []),
                this.orm.searchRead(stopModel, [], ["duration"]),
                this.orm.searchRead(
                    tripModel,
                    [],
                    ["name", "start_date", "end_date", "state", "stop_count"],
                    {limit: 5, order: "start_date desc, id desc"},
                ),
            ]);

            this.state.metrics = {
                totalTrips,
                draftTrips,
                plannedTrips,
                completedTrips,
                cancelledTrips,
                totalCities,
                totalStops,
                totalDays: stopDurations.reduce((total, stop) => total + stop.duration, 0),
            };
            this.state.recentTrips = recentTrips;
        } catch (error) {
            console.error("Unable to load the GlobeTrotter dashboard", error);
            this.state.error = true;
        } finally {
            this.state.loading = false;
        }
    }

    openModel(model, domain = []) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: model,
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }

    openTrip(trip) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "globetrotter.trip",
            views: [[false, "form"]],
            res_id: trip.id,
        });
    }

    formatDate(value) {
        if (!value) {
            return "-";
        }
        return value;
    }

    statusLabel(state) {
        return {
            draft: "Draft",
            planned: "Planned",
            completed: "Completed",
            cancelled: "Cancelled",
        }[state] || state;
    }
}

registry.category("actions").add("globetrotter.dashboard", GlobeTrotterDashboard);
