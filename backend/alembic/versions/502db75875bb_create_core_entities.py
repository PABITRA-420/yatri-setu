"""create_core_entities

Revision ID: 502db75875bb
Revises: 
Create Date: 2026-09-07 19:18:54.856117

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '502db75875bb'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Creates all 17 core Yatri Setu platform tables."""
    # 1. destinations
    op.create_table(
        'destinations',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('state', sa.String(length=64), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('geom_wkt', sa.String(length=128), nullable=True),
        sa.Column('carrying_capacity', sa.Integer(), nullable=True, default=5000),
        sa.Column('current_pressure', sa.Float(), nullable=True, default=20.0),
        sa.Column('is_rural', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_destinations_id'), 'destinations', ['id'], unique=False)

    # 2. attractions
    op.create_table(
        'attractions',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('destination_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=True, default='scenic'),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('geom_wkt', sa.String(length=128), nullable=True),
        sa.Column('capacity_per_hour', sa.Integer(), nullable=True, default=500),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_attractions_destination_id'), 'attractions', ['destination_id'], unique=False)
    op.create_index(op.f('ix_attractions_id'), 'attractions', ['id'], unique=False)

    # 3. hosts
    op.create_table(
        'hosts',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('full_name', sa.String(length=128), nullable=False),
        sa.Column('phone', sa.String(length=32), nullable=False),
        sa.Column('panchayat_name', sa.String(length=128), nullable=False),
        sa.Column('village', sa.String(length=128), nullable=False),
        sa.Column('state', sa.String(length=64), nullable=False),
        sa.Column('verification_status', sa.String(length=32), nullable=True, default='VERIFIED'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hosts_id'), 'hosts', ['id'], unique=False)

    # 4. homestays
    op.create_table(
        'homestays',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('host_id', sa.String(length=64), nullable=False),
        sa.Column('destination_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=True),
        sa.Column('tagline', sa.String(length=256), nullable=True),
        sa.Column('address', sa.String(length=256), nullable=True),
        sa.Column('room_type', sa.String(length=64), nullable=True, default='Standard Room'),
        sa.Column('total_rooms', sa.Integer(), nullable=True, default=2),
        sa.Column('max_guests', sa.Integer(), nullable=True, default=6),
        sa.Column('price_per_night', sa.Float(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('rating', sa.Float(), nullable=True, default=5.0),
        sa.Column('reviews_count', sa.Integer(), nullable=True, default=0),
        sa.Column('panchayat_verified', sa.Boolean(), nullable=True, default=True),
        sa.Column('verification_status', sa.String(length=32), nullable=True, default='VERIFIED'),
        sa.Column('is_published', sa.Boolean(), nullable=True, default=True),
        sa.Column('village', sa.String(length=128), nullable=True),
        sa.Column('panchayat_name', sa.String(length=128), nullable=True),
        sa.Column('special_activity', sa.String(length=256), nullable=True),
        sa.Column('amenities_json', sa.JSON(), nullable=True),
        sa.Column('images_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id']),
        sa.ForeignKeyConstraint(['host_id'], ['hosts.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_homestays_destination_id'), 'homestays', ['destination_id'], unique=False)
    op.create_index(op.f('ix_homestays_host_id'), 'homestays', ['host_id'], unique=False)
    op.create_index(op.f('ix_homestays_id'), 'homestays', ['id'], unique=False)

    # 5. experiences
    op.create_table(
        'experiences',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('destination_id', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=True, default='cultural'),
        sa.Column('price_inr', sa.Float(), nullable=False),
        sa.Column('duration_hours', sa.Float(), nullable=True, default=2.5),
        sa.Column('sustainability_score', sa.Float(), nullable=True, default=90.0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_experiences_destination_id'), 'experiences', ['destination_id'], unique=False)
    op.create_index(op.f('ix_experiences_id'), 'experiences', ['id'], unique=False)

    # 6. bookings
    op.create_table(
        'bookings',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('homestay_id', sa.String(length=64), nullable=False),
        sa.Column('destination_id', sa.String(length=64), nullable=False),
        sa.Column('guest_name', sa.String(length=128), nullable=False),
        sa.Column('traveler_phone', sa.String(length=32), nullable=True),
        sa.Column('traveler_email', sa.String(length=128), nullable=True),
        sa.Column('emergency_contact', sa.String(length=32), nullable=True),
        sa.Column('check_in_date', sa.Date(), nullable=False),
        sa.Column('check_out_date', sa.Date(), nullable=False),
        sa.Column('guests_count', sa.Integer(), nullable=True, default=2),
        sa.Column('rooms_booked', sa.Integer(), nullable=True, default=1),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('host_earning', sa.Float(), nullable=False),
        sa.Column('platform_fee', sa.Float(), nullable=False),
        sa.Column('community_fund', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=True, default='CONFIRMED'),
        sa.Column('failure_reason', sa.String(length=64), nullable=True),
        sa.Column('failure_detail', sa.Text(), nullable=True),
        sa.Column('idempotency_key', sa.String(length=128), nullable=True),
        sa.Column('digital_pass_qr_payload', sa.Text(), nullable=True),
        sa.Column('transitions_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id']),
        sa.ForeignKeyConstraint(['homestay_id'], ['homestays.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bookings_destination_id'), 'bookings', ['destination_id'], unique=False)
    op.create_index(op.f('ix_bookings_homestay_id'), 'bookings', ['homestay_id'], unique=False)
    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False)
    op.create_index(op.f('ix_bookings_idempotency_key'), 'bookings', ['idempotency_key'], unique=False)

    # 7. availability
    op.create_table(
        'availability',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('homestay_id', sa.String(length=64), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('total_units', sa.Integer(), nullable=True, default=2),
        sa.Column('booked_units', sa.Integer(), nullable=True, default=0),
        sa.Column('is_available', sa.Boolean(), nullable=True, default=True),
        sa.Column('rooms_available', sa.Integer(), nullable=True, default=1),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['homestay_id'], ['homestays.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('homestay_id', 'date', name='uq_homestay_date_inventory')
    )
    op.create_index(op.f('ix_availability_date'), 'availability', ['date'], unique=False)
    op.create_index(op.f('ix_availability_homestay_id'), 'availability', ['homestay_id'], unique=False)
    op.create_index(op.f('ix_availability_id'), 'availability', ['id'], unique=False)

    # 8. crowd_observations
    op.create_table(
        'crowd_observations',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('destination_id', sa.String(length=64), nullable=False),
        sa.Column('signal_type', sa.String(length=64), nullable=False),
        sa.Column('raw_value', sa.Float(), nullable=False),
        sa.Column('normalized_value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=32), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('source', sa.String(length=128), nullable=False),
        sa.Column('provider_mode', sa.String(length=16), nullable=True, default='MOCK'),
        sa.Column('confidence', sa.Float(), nullable=True, default=0.9),
        sa.Column('data_quality', sa.String(length=16), nullable=True, default='HIGH'),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crowd_observations_destination_id'), 'crowd_observations', ['destination_id'], unique=False)
    op.create_index(op.f('ix_crowd_observations_id'), 'crowd_observations', ['id'], unique=False)
    op.create_index(op.f('ix_crowd_observations_signal_type'), 'crowd_observations', ['signal_type'], unique=False)
    op.create_index(op.f('ix_crowd_observations_timestamp'), 'crowd_observations', ['timestamp'], unique=False)

    # 9. crowd_predictions
    op.create_table(
        'crowd_predictions',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('destination_id', sa.String(length=64), nullable=False),
        sa.Column('prediction_date', sa.Date(), nullable=False),
        sa.Column('predicted_pressure', sa.Float(), nullable=False),
        sa.Column('actual_pressure', sa.Float(), nullable=True),
        sa.Column('absolute_error', sa.Float(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.Column('evaluated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crowd_predictions_destination_id'), 'crowd_predictions', ['destination_id'], unique=False)
    op.create_index(op.f('ix_crowd_predictions_id'), 'crowd_predictions', ['id'], unique=False)
    op.create_index(op.f('ix_crowd_predictions_prediction_date'), 'crowd_predictions', ['prediction_date'], unique=False)

    # 10. weather_observations
    op.create_table(
        'weather_observations',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('destination_id', sa.String(length=64), nullable=False),
        sa.Column('temperature_c', sa.Float(), nullable=False),
        sa.Column('condition', sa.String(length=64), nullable=False),
        sa.Column('comfort_index', sa.Float(), nullable=True, default=80.0),
        sa.Column('provider_mode', sa.String(length=16), nullable=True, default='MOCK'),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_weather_observations_destination_id'), 'weather_observations', ['destination_id'], unique=False)
    op.create_index(op.f('ix_weather_observations_id'), 'weather_observations', ['id'], unique=False)

    # 11. traffic_observations
    op.create_table(
        'traffic_observations',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('destination_id', sa.String(length=64), nullable=False),
        sa.Column('corridor_name', sa.String(length=128), nullable=False),
        sa.Column('delay_minutes', sa.Float(), nullable=True, default=0.0),
        sa.Column('congestion_level', sa.String(length=32), nullable=True, default='NORMAL'),
        sa.Column('provider_mode', sa.String(length=16), nullable=True, default='MOCK'),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_traffic_observations_destination_id'), 'traffic_observations', ['destination_id'], unique=False)
    op.create_index(op.f('ix_traffic_observations_id'), 'traffic_observations', ['id'], unique=False)

    # 12. demand_observations
    op.create_table(
        'demand_observations',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('destination_id', sa.String(length=64), nullable=False),
        sa.Column('search_count', sa.Integer(), nullable=True, default=100),
        sa.Column('unique_searchers', sa.Integer(), nullable=True, default=80),
        sa.Column('booking_conversion', sa.Float(), nullable=True, default=0.12),
        sa.Column('period_change_percent', sa.Float(), nullable=True, default=5.0),
        sa.Column('trend', sa.String(length=32), nullable=True, default='STABLE'),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_demand_observations_destination_id'), 'demand_observations', ['destination_id'], unique=False)
    op.create_index(op.f('ix_demand_observations_id'), 'demand_observations', ['id'], unique=False)

    # 13. events
    op.create_table(
        'events',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('destination_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('expected_footfall', sa.Integer(), nullable=True, default=1000),
        sa.Column('radius_km', sa.Float(), nullable=True, default=10.0),
        sa.Column('category', sa.String(length=64), nullable=True, default='cultural'),
        sa.Column('source', sa.String(length=128), nullable=True, default='District Tourism Office'),
        sa.Column('confidence', sa.Float(), nullable=True, default=0.9),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_destination_id'), 'events', ['destination_id'], unique=False)
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)

    # 14. holidays
    op.create_table(
        'holidays',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('holiday_type', sa.String(length=32), nullable=True, default='NATIONAL'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('surge_multiplier', sa.Float(), nullable=True, default=1.3),
        sa.Column('applicable_states', sa.String(length=128), nullable=True, default='West Bengal, Sikkim'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_holidays_id'), 'holidays', ['id'], unique=False)

    # 15. interventions
    op.create_table(
        'interventions',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('destination_id', sa.String(length=64), nullable=False),
        sa.Column('intervention_type', sa.String(length=64), nullable=False),
        sa.Column('intensity', sa.Float(), nullable=True, default=0.5),
        sa.Column('target_absorber_id', sa.String(length=64), nullable=True),
        sa.Column('simulated_reduction', sa.Float(), nullable=True, default=0.0),
        sa.Column('redirected_visitors', sa.Integer(), nullable=True, default=0),
        sa.Column('economic_gain_inr', sa.Float(), nullable=True, default=0.0),
        sa.Column('applied_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interventions_destination_id'), 'interventions', ['destination_id'], unique=False)
    op.create_index(op.f('ix_interventions_id'), 'interventions', ['id'], unique=False)

    # 16. safety_incidents
    op.create_table(
        'safety_incidents',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('destination_id', sa.String(length=64), nullable=False),
        sa.Column('trip_id', sa.String(length=64), nullable=True),
        sa.Column('traveler_session_id', sa.String(length=128), nullable=True),
        sa.Column('user_name', sa.String(length=128), nullable=True),
        sa.Column('user_phone', sa.String(length=32), nullable=True),
        sa.Column('incident_type', sa.String(length=64), nullable=True, default='SOS'),
        sa.Column('severity', sa.String(length=32), nullable=True, default='HIGH'),
        sa.Column('status', sa.String(length=32), nullable=True, default='DELIVERED'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('resolved', sa.Boolean(), nullable=True, default=False),
        sa.Column('escalation_level', sa.Integer(), nullable=True, default=0),
        sa.Column('idempotency_key', sa.String(length=128), nullable=True),
        sa.Column('audit_trail_json', sa.JSON(), nullable=True),
        sa.Column('notifications_json', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_safety_incidents_destination_id'), 'safety_incidents', ['destination_id'], unique=False)
    op.create_index(op.f('ix_safety_incidents_id'), 'safety_incidents', ['id'], unique=False)
    op.create_index(op.f('ix_safety_incidents_idempotency_key'), 'safety_incidents', ['idempotency_key'], unique=False)
    op.create_index(op.f('ix_safety_incidents_user_phone'), 'safety_incidents', ['user_phone'], unique=False)

    # 17. demand_events
    op.create_table(
        'demand_events',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('destination_id', sa.String(length=64), nullable=True),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('session_id', sa.String(length=128), nullable=True),
        sa.Column('user_id', sa.String(length=128), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('source', sa.String(length=128), nullable=False, default='YATRI_SETU_NETWORK'),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_demand_events_destination_id'), 'demand_events', ['destination_id'], unique=False)
    op.create_index(op.f('ix_demand_events_event_type'), 'demand_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_demand_events_id'), 'demand_events', ['id'], unique=False)
    op.create_index(op.f('ix_demand_events_session_id'), 'demand_events', ['session_id'], unique=False)
    op.create_index(op.f('ix_demand_events_timestamp'), 'demand_events', ['timestamp'], unique=False)
    op.create_index(op.f('ix_demand_events_user_id'), 'demand_events', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema: Drops all 17 tables in reverse dependency order."""
    op.drop_table('demand_events')
    op.drop_table('safety_incidents')
    op.drop_table('interventions')
    op.drop_table('holidays')
    op.drop_table('events')
    op.drop_table('demand_observations')
    op.drop_table('traffic_observations')
    op.drop_table('weather_observations')
    op.drop_table('crowd_predictions')
    op.drop_table('crowd_observations')
    op.drop_table('availability')
    op.drop_table('bookings')
    op.drop_table('experiences')
    op.drop_table('homestays')
    op.drop_table('hosts')
    op.drop_table('attractions')
    op.drop_table('destinations')
