"""
Conversion Funnel Service for Yatri Setu (Milestone 7E).
Aggregates first-party user intent telemetry into transparent conversion funnels,
calculating observed alternative acceptance rates and per-destination booking metrics.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from app.core.config import settings
from app.data.seed_data import DESTINATIONS_DATA
from app.services.demand_aggregation_service import demand_aggregation_service
from app.models.demand import DemandEventType
from app.services.conversion.schemas import (
    AcceptanceRateMode,
    DestinationConversionMetrics,
    FunnelStageCount,
    ConversionSummaryResponse,
)


class ConversionFunnelService:
    def get_destination_conversion_metrics(
        self,
        destination_id: Optional[str] = None
    ) -> List[DestinationConversionMetrics]:
        """Calculates conversion counts and rates per destination from authoritative events."""
        raw_events = demand_aggregation_service._events

        dest_ids = [destination_id.lower().strip()] if destination_id else [d["id"] for d in DESTINATIONS_DATA]
        results = []

        for d_id in dest_ids:
            dest_obj = next((d for d in DESTINATIONS_DATA if d["id"] == d_id), None)
            d_name = dest_obj["name"] if dest_obj else d_id.capitalize()

            # Filter events for this destination
            events = [e for e in raw_events if e.get("destination_id") == d_id]

            searches = len([e for e in events if e.get("event_type") == DemandEventType.SEARCH.value])
            date_selections = len([e for e in events if e.get("event_type") == DemandEventType.DATE_SELECTED.value])
            alt_views = len([e for e in events if e.get("event_type") == DemandEventType.ALTERNATIVE_VIEWED.value])
            alt_accepts = len([e for e in events if e.get("event_type") == DemandEventType.ALTERNATIVE_ACCEPTANCE.value])
            avail_checks = len([
                e for e in events
                if e.get("event_type") in (DemandEventType.AVAILABILITY.value, DemandEventType.AVAILABILITY_CHECKED.value)
            ])
            booking_inits = len([e for e in events if e.get("event_type") == DemandEventType.BOOKING_INITIATED.value])
            booking_confirms = len([
                e for e in events
                if e.get("event_type") in (DemandEventType.BOOKING.value, DemandEventType.BOOKING_CONFIRMED.value)
                and (e.get("metadata") or {}).get("status") != "FAILED"
            ])
            booking_cancels = len([e for e in events if e.get("event_type") == DemandEventType.BOOKING_CANCELLED.value])
            outbound_clicks = len([e for e in events if e.get("event_type") == DemandEventType.OUTBOUND_BOOKING_CLICK.value])

            # Rates with explicit non-zero denominators
            s_to_avail = round(avail_checks / max(1, searches), 4) if searches > 0 else 0.0
            avail_to_book = round(booking_inits / max(1, avail_checks), 4) if avail_checks > 0 else 0.0
            book_to_confirm = round(booking_confirms / max(1, booking_inits), 4) if booking_inits > 0 else (1.0 if booking_confirms > 0 else 0.0)
            alt_acc_rate = round(alt_accepts / max(1, alt_views), 4) if alt_views > 0 else (round(alt_accepts / max(1, searches), 4) if searches > 0 else 0.0)
            cancel_rate = round(booking_cancels / max(1, booking_confirms), 4) if booking_confirms > 0 else 0.0

            results.append(
                DestinationConversionMetrics(
                    destination_id=d_id,
                    destination_name=d_name,
                    searches=searches,
                    date_selections=date_selections,
                    alternative_views=alt_views,
                    alternative_acceptances=alt_accepts,
                    availability_checks=avail_checks,
                    booking_initiations=booking_inits,
                    booking_confirmations=booking_confirms,
                    booking_cancellations=booking_cancels,
                    outbound_clicks=outbound_clicks,
                    search_to_availability_rate=s_to_avail,
                    availability_to_booking_rate=avail_to_book,
                    booking_to_confirmation_rate=min(1.0, book_to_confirm),
                    alternative_acceptance_rate=min(1.0, alt_acc_rate),
                    cancellation_rate=min(1.0, cancel_rate)
                )
            )

        return results

    def get_funnel(self) -> List[FunnelStageCount]:
        """Builds normalized step-by-step circuit conversion funnel."""
        raw_events = demand_aggregation_service._events

        searches = len([e for e in raw_events if e.get("event_type") == DemandEventType.SEARCH.value])
        alt_views = len([e for e in raw_events if e.get("event_type") == DemandEventType.ALTERNATIVE_VIEWED.value])
        alt_accepts = len([e for e in raw_events if e.get("event_type") == DemandEventType.ALTERNATIVE_ACCEPTANCE.value])
        avail_checks = len([
            e for e in raw_events
            if e.get("event_type") in (DemandEventType.AVAILABILITY.value, DemandEventType.AVAILABILITY_CHECKED.value)
        ])
        booking_inits = len([e for e in raw_events if e.get("event_type") == DemandEventType.BOOKING_INITIATED.value])
        booking_confirms = len([
            e for e in raw_events
            if e.get("event_type") in (DemandEventType.BOOKING.value, DemandEventType.BOOKING_CONFIRMED.value)
            and (e.get("metadata") or {}).get("status") != "FAILED"
        ])

        stages = [
            ("SEARCH", searches),
            ("ALTERNATIVE_VIEW", alt_views),
            ("ALTERNATIVE_ACCEPT", alt_accepts),
            ("AVAILABILITY_CHECK", avail_checks),
            ("BOOKING_INITIATED", booking_inits),
            ("BOOKING_CONFIRMED", booking_confirms),
        ]

        funnel: List[FunnelStageCount] = []
        top_count = max(1, searches)

        for idx, (name, count) in enumerate(stages):
            if idx == 0:
                conv_prev = 100.0 if searches > 0 else 0.0
                conv_top = 100.0 if searches > 0 else 0.0
            else:
                prev_count = stages[idx - 1][1]
                conv_prev = round((count / max(1, prev_count)) * 100.0, 1) if prev_count > 0 else 0.0
                conv_top = round((count / top_count) * 100.0, 1) if searches > 0 else 0.0

            funnel.append(FunnelStageCount(
                stage=name,
                count=count,
                conversion_from_previous=min(100.0, conv_prev),
                conversion_from_top=min(100.0, conv_top)
            ))

        return funnel

    def get_conversion_summary(self) -> ConversionSummaryResponse:
        """Returns macro conversion intelligence overview across all circuit destinations."""
        dest_metrics = self.get_destination_conversion_metrics()

        tot_search = sum(m.searches for m in dest_metrics)
        tot_date = sum(m.date_selections for m in dest_metrics)
        tot_views = sum(m.alternative_views for m in dest_metrics)
        tot_accepts = sum(m.alternative_acceptances for m in dest_metrics)
        tot_avail = sum(m.availability_checks for m in dest_metrics)
        tot_inits = sum(m.booking_initiations for m in dest_metrics)
        tot_confirms = sum(m.booking_confirmations for m in dest_metrics)
        tot_cancels = sum(m.booking_cancellations for m in dest_metrics)
        tot_outbound = sum(m.outbound_clicks for m in dest_metrics)

        circuit_metrics = DestinationConversionMetrics(
            destination_id="circuit-all",
            destination_name="Eastern Himalayan Circuit",
            searches=tot_search,
            date_selections=tot_date,
            alternative_views=tot_views,
            alternative_acceptances=tot_accepts,
            availability_checks=tot_avail,
            booking_initiations=tot_inits,
            booking_confirmations=tot_confirms,
            booking_cancellations=tot_cancels,
            outbound_clicks=tot_outbound,
            search_to_availability_rate=round(tot_avail / max(1, tot_search), 4) if tot_search > 0 else 0.0,
            availability_to_booking_rate=round(tot_inits / max(1, tot_avail), 4) if tot_avail > 0 else 0.0,
            booking_to_confirmation_rate=round(tot_confirms / max(1, tot_inits), 4) if tot_inits > 0 else 0.0,
            alternative_acceptance_rate=round(tot_accepts / max(1, tot_views), 4) if tot_views > 0 else 0.0,
            cancellation_rate=round(tot_cancels / max(1, tot_confirms), 4) if tot_confirms > 0 else 0.0
        )

        funnel = self.get_funnel()

        # Observed acceptance rate calculation
        sample_size = tot_views or tot_search
        configured_rate = settings.REDIRECTION_ACCEPTANCE_RATE

        if sample_size >= 20 and tot_accepts > 0:
            observed_rate = round(tot_accepts / max(1, sample_size), 3)
            mode = AcceptanceRateMode.OBSERVED
        elif sample_size > 0 and tot_accepts > 0:
            observed_rate = round(tot_accepts / max(1, sample_size), 3)
            mode = AcceptanceRateMode.INSUFFICIENT_DATA
        else:
            observed_rate = configured_rate
            mode = AcceptanceRateMode.CONFIGURED

        warning = None
        if tot_confirms > tot_inits and tot_inits > 0:
            warning = "DATA_QUALITY_WARNING: Confirmed bookings exceed initiations due to baseline batch seeds."

        return ConversionSummaryResponse(
            circuit_metrics=circuit_metrics,
            destination_metrics=dest_metrics,
            funnel=funnel,
            observed_acceptance_rate=observed_rate,
            configured_acceptance_rate=configured_rate,
            acceptance_rate_mode=mode,
            sample_size=sample_size,
            data_quality_warning=warning,
            provenance="REAL — YATRI SETU NETWORK",
            generated_at=datetime.utcnow().isoformat()
        )


conversion_funnel_service = ConversionFunnelService()
