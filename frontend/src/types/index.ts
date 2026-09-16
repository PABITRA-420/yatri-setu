export type CrowdLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'VERY HIGH';

export interface Coordinates {
  lat: number;
  lng: number;
}

export interface Attraction {
  id: string;
  name: string;
  category: string;
  description: string;
  crowd_density: string;
  visit_duration_hrs: number;
  best_time: string;
  image_url: string;
}

export interface DestinationAttributes {
  nature: number;
  climate: string;
  activities: string[];
  culture: string;
  budget_level: string;
  avg_cost_per_day_inr: number;
  accessibility: string;
  altitude_ft: number;
}

export interface Destination {
  id: string;
  name: string;
  tagline: string;
  region: string;
  state: string;
  description: string;
  coordinates: { lat: number; lng: number };
  hero_image: string;
  gallery_images: string[];
  attributes: DestinationAttributes;
  highlights: string[];
  attractions: Attraction[];
  base_crowd_score: number;
  recommended_duration_days: number;
  tags: string[];
}

export interface DestinationSummary {
  id: string;
  name: string;
  tagline: string;
  region: string;
  state: string;
  hero_image: string;
  crowd_score: number;
  crowd_level: CrowdLevel;
  avg_cost_per_day_inr: number;
  tags: string[];
  distance_from_query_km?: number;
}

export interface CrowdFactorItem {
  name: string;
  key: string;
  raw_value: number;
  weight_percentage: number;
  weighted_contribution: number;
  description: string;
}

export interface CrowdResponse {
  destination_id: string;
  destination_name: string;
  crowd_score: number;
  crowd_level: CrowdLevel;
  color_code: string;
  summary: string;
  why_crowded: string[];
  bottlenecks: string[];
  peak_visiting_hours: string;
  best_time_to_visit_today: string;
  factors: CrowdFactorItem[];
  live_traffic_status: string;
  hotel_occupancy_rate: string;
  last_updated: string;
}

export interface AlternativeRecommendation {
  id: string;
  name: string;
  tagline: string;
  state: string;
  hero_image: string;
  crowd_score: number;
  crowd_level: CrowdLevel;
  similarity_score: number;
  original_crowd_score: number;
  alternative_crowd_score: number;
  crowd_reduction_percent: number;
  distance_km: number;
  estimated_cost_per_day: number;
  cost_difference_percent: number;
  reasons_to_recommend: string[];
  shared_highlights: string[];
  matching_attributes: string[];
  key_experience: string;
  eco_tag: string;
}

export interface AlternativesResponse {
  origin_destination_id: string;
  origin_destination_name: string;
  origin_crowd_score: number;
  origin_crowd_level: CrowdLevel;
  alternatives: AlternativeRecommendation[];
}

export interface DateAlternativeRecommendation {
  start_date: string;
  end_date: string;
  window_label: string;
  crowd_score: number;
  crowd_classification: CrowdLevel;
  crowd_reduction_percent: number;
  estimated_cost_change: string;
  availability_score: number;
  reason: string;
}

export interface DateAlternativesResponse {
  destination_id: string;
  destination_name: string;
  preferred_start_date: string;
  preferred_end_date: string;
  preferred_crowd_score: number;
  preferred_crowd_classification: CrowdLevel;
  date_alternatives: DateAlternativeRecommendation[];
}

export interface DestinationDecisionResponse {
  selected_destination: string;
  destination_id: string;
  selected_dates: string;
  crowd_status: CrowdLevel;
  crowd_score: number;
  alerts: string[];
  alternative_destinations: AlternativeRecommendation[];
  alternative_dates: DateAlternativeRecommendation[];
  recommended_action: 'KEEP_DESTINATION' | 'CHANGE_DATES' | 'CHANGE_DESTINATION';
}

export interface WeatherForecast {
  destination_id: string;
  destination_name: string;
  temperature_range_c: string;
  temp_min_c: number;
  temp_max_c: number;
  condition: string;
  precipitation_chance_percent: number;
  rain_expected: boolean;
  mountain_visibility_score: number;
  advisory: string;
  best_hours_for_outdoors: string;
  is_demo_forecast?: boolean;
  provider_source?: string;
}

export interface TourismImpact {
  estimated_local_spend_inr: number;
  direct_village_economy_percent: number;
  local_businesses_supported: number;
  crowd_pressure_reduction_percent: number;
  community_fund_contribution_inr: number;
  carbon_saved_vs_private_car_kg: number;
}

export interface SustainabilityFactor {
  name: string;
  category: string;
  points_earned: number;
  max_points: number;
  description: string;
}

export interface SustainabilityScorecard {
  sustainability_score: number;
  sustainability_classification: string;
  factors: SustainabilityFactor[];
  tourism_impact: TourismImpact;
  eco_summary: string;
}

export interface ActivitySlot {
  time_slot: string;
  period: 'Morning' | 'Afternoon' | 'Evening';
  title: string;
  description: string;
  location_name: string;
  crowd_forecast: string;
  cost_estimate_inr: number;
  duration_hrs: number;
  travel_tip?: string;
  category: string;
  image_url?: string;
  is_weather_adapted?: boolean;
  adaptation_reason?: string;
}

export interface ItineraryDay {
  day_number: number;
  theme: string;
  overview: string;
  estimated_budget_inr: number;
  activities: ActivitySlot[];
  transit_advice: string;
}

export interface ItineraryResponse {
  itinerary_id: string;
  destination_id: string;
  destination_name: string;
  duration_days: number;
  traveler_type: string;
  pace: string;
  interests: string[];
  total_estimated_budget_inr: number;
  crowd_avoidance_rating: string;
  local_economic_impact_tag: string;
  days: ItineraryDay[];
  ai_generated_note: string;
  sustainability_score?: number;
  sustainability_classification?: string;
  tourism_impact?: TourismImpact;
  weather_forecast?: WeatherForecast;
  weather_adaptation_notice?: string;
  why_this_itinerary?: string[];
  ai_provider_used?: string;
  optimization_history?: string[];
}

export interface ItineraryOptimizeRequest {
  itinerary_id: string;
  destination_id: string;
  instruction: string;
  custom_instruction?: string;
  current_itinerary?: ItineraryResponse;
}

export interface HostInfo {
  name: string;
  avatar_url: string;
  experience_years: number;
  languages: string[];
  about: string;
  verified_panchayat: boolean;
  response_rate: string;
}

export interface Homestay {
  id: string;
  destination_id: string;
  destination_name: string;
  title: string;
  tagline: string;
  address: string;
  price_per_night_inr: number;
  rating: number;
  reviews_count: number;
  room_type: string;
  max_guests: number;
  amenities: string[];
  images: string[];
  host: HostInfo;
  community_fund_contribution_percent: number;
  special_activity: string;
  verified: boolean;
  panchayat_verified?: boolean;
  sustainable_stay_badge?: boolean;
}

export interface HomestayBookingResponse {
  booking_id: string;
  homestay: Homestay;
  traveler_name: string;
  traveler_phone: string;
  check_in_date: string;
  check_out_date: string;
  number_of_guests: number;
  total_nights: number;
  subtotal_inr: number;
  discount_inr?: number;
  green_credits_redeemed?: number;
  community_fund_contribution_inr: number;
  total_amount_inr: number;
  platform_fee_inr?: number;
  host_earning_inr?: number;
  payment_status?: string;
  status: string;
  digital_pass_qr_payload: string;
  host_contact: string;
  homestay_gps: string;
  created_at: string;
}

// Milestone 3: Rural Tourism Ecosystem Types

export interface VerificationEvent {
  status: string;
  timestamp: string;
  actor: string;
  notes: string;
}

export interface HostVerification {
  status: 'SUBMITTED' | 'UNDER_REVIEW' | 'VERIFIED' | 'REJECTED' | 'PUBLISHED';
  id_proof_type: string;
  id_proof_number_masked: string;
  panchayat_name: string;
  block: string;
  district: string;
  submitted_at: string;
  verified_at?: string;
  reviewed_by?: string;
  review_notes?: string;
  history: VerificationEvent[];
}

export interface Host {
  id: string;
  name: string;
  phone: string;
  email: string;
  village: string;
  panchayat_name: string;
  languages: string[];
  bio: string;
  avatar_url: string;
  experience_years: number;
  verification: HostVerification;
  created_at: string;
}

export interface HomestayListing {
  id: string;
  host_id: string;
  destination_id: string;
  destination_name: string;
  title: string;
  tagline: string;
  address: string;
  village: string;
  panchayat_name: string;
  price_per_night_inr: number;
  room_type: string;
  max_guests: number;
  rooms_count: number;
  amenities: string[];
  sustainability_attributes: string[];
  images: string[];
  special_activity: string;
  rating: number;
  reviews_count: number;
  verification_status: 'SUBMITTED' | 'UNDER_REVIEW' | 'VERIFIED' | 'REJECTED' | 'PUBLISHED';
  is_published: boolean;
  community_fund_contribution_percent: number;
}

export interface AvailabilityRecord {
  homestay_id: string;
  date: string;
  is_available: boolean;
  price_override_inr?: number;
  blocked_reason?: string;
}

export interface HostEarningBreakdown {
  booking_id: string;
  homestay_id: string;
  homestay_name: string;
  guest_name: string;
  check_in_date: string;
  check_out_date: string;
  nights: number;
  gross_booking_value: number;
  platform_fee: number;
  community_fund_contribution: number;
  net_host_earning: number;
  payout_status: string;
  created_at: string;
}

export interface HostEarningsSummary {
  host_id: string;
  total_bookings: number;
  gross_value_inr: number;
  platform_fee_inr: number;
  community_contribution_inr: number;
  net_host_income_inr: number;
  records: HostEarningBreakdown[];
}

export interface HostOnboardingRequest {
  name: string;
  phone: string;
  email: string;
  village: string;
  panchayat_name: string;
  destination_id: string;
  languages: string[];
  bio: string;
  homestay_title: string;
  tagline: string;
  address: string;
  room_type: string;
  rooms_count: number;
  max_guests: number;
  price_per_night_inr: number;
  amenities: string[];
  sustainability_attributes: string[];
  special_activity: string;
}

export interface VoiceDraftResponse {
  original_transcript: string;
  suggested_title: string;
  suggested_tagline: string;
  detected_destination_id: string;
  detected_village: string;
  detected_room_type: string;
  suggested_rooms_count: number;
  detected_amenities: string[];
  detected_sustainability_attributes: string[];
  suggested_experiences: string[];
  price_requires_host_input: boolean;
  verification_status: string;
  warning_guardrail: string;
}

export interface Experience {
  id: string;
  title: string;
  description: string;
  host_id: string;
  host_name: string;
  destination_id: string;
  destination_name: string;
  village: string;
  panchayat_name: string;
  duration_hours: number;
  price_inr: number;
  capacity: number;
  languages: string[];
  sustainability_score: number;
  verification_status: string;
  category: string;
  image_url: string;
  highlights: string[];
  gear_provided: string[];
}

export interface ExperienceCreateRequest {
  title: string;
  description: string;
  host_id: string;
  destination_id: string;
  duration_hours: number;
  price_inr: number;
  capacity: number;
  languages: string[];
  category: string;
  image_url?: string;
  highlights?: string[];
}

export interface CommunityFundProject {
  id: string;
  title: string;
  category: string;
  budget_inr: number;
  status: 'COMPLETED' | 'IN_PROGRESS' | 'PROPOSED';
  completion_date: string;
  impact_description: string;
}

export interface PanchayatVerificationItem {
  listing_id: string;
  host_id: string;
  host_name: string;
  host_phone: string;
  homestay_title: string;
  destination_id: string;
  destination_name: string;
  village: string;
  panchayat_name: string;
  submitted_at: string;
  verification_status: 'SUBMITTED' | 'UNDER_REVIEW' | 'VERIFIED' | 'REJECTED' | 'PUBLISHED';
  id_proof_type: string;
  id_proof_masked: string;
  rooms_count: number;
  price_per_night_inr: number;
  amenities: string[];
  sustainability_attributes: string[];
  history: VerificationEvent[];
}

export interface PanchayatDecisionRequest {
  action: 'APPROVE' | 'REJECT';
  reason: string;
  reviewer_name: string;
}

export interface PanchayatDecisionResponse {
  listing_id: string;
  previous_status: string;
  new_status: string;
  updated_at: string;
  reviewer_name: string;
  decision_notes: string;
}

export interface PanchayatDashboard {
  panchayat_name: string;
  block: string;
  district: string;
  state: string;
  verified_homestays_count: number;
  pending_verifications_count: number;
  local_guides_count: number;
  total_experiences_count: number;
  tourist_arrivals_this_month: number;
  local_booking_revenue_inr: number;
  community_fund_balance_inr: number;
  tourism_pressure_relief_index: number;
  community_projects: CommunityFundProject[];
  recent_verifications: PanchayatVerificationItem[];
}

export interface DestinationFlowImpact {
  destination_id: string;
  destination_name: string;
  is_congested_hub: boolean;
  redirected_tourists_count: number;
  estimated_bookings: number;
  estimated_local_revenue_inr: number;
  experience_bookings: number;
  crowd_pressure_reduction_percent: number;
  community_fund_generated_inr: number;
  beneficiary_villages: string[];
  narrative_summary: string;
  key_metrics: Array<{
    label: string;
    value: string;
    sub: string;
  }>;
}

export interface ResponderInfo {
  name: string;
  agency: string;
  distance_km: number;
  eta_minutes: number;
  phone: string;
  status: string;
}

export interface SosAlertResponse {
  alert_id: string;
  status: string;
  timestamp: string;
  user_name: string;
  user_phone: string;
  gps_coordinates: string;
  nearest_responders: ResponderInfo[];
  national_helplines: Array<{ service: string; number: string; toll_free: boolean }>;
  instructions_for_traveler: string[];
  beacon_signal_strength: string;
}

export interface TripDetailsResponse {
  trip_id: string;
  destination_name: string;
  destination_id: string;
  homestay_name: string;
  dates: string;
  status: string;
  travelers_count: number;
  digital_pass_code: string;
  emergency_pin_active: boolean;
  weather_alert: string;
  host_support_number: string;
  local_panchayat_contact: string;
  check_in_location: string;
  packing_checklist: string[];
}

// Milestone 4: Destination Pressure Intelligence & Command Center

export type PressureLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';

export interface DestinationSignal {
  signal_key: string;
  signal_name: string;
  weight: number;
  value: number;
  weighted_score: number;
  available: boolean;
  source: string;
  confidence: number;
  raw_value?: number | null;
  unit: string;
  notes: string;
}

export interface PressureResponse {
  destination_id: string;
  destination_name: string;
  pressure_score: number;
  pressure_level: PressureLevel;
  color_code: string;
  confidence_score: number;
  confidence_percent: number;
  signals_available: number;
  total_signals: number;
  signals: DestinationSignal[];
  advisory: string;
  recommended_action: string;
  carrying_capacity_percent: number;
  peak_hours: string;
  best_time_to_visit: string;
  timestamp: string;
}

export interface PressureDayForecast {
  date: string;
  day_name: string;
  predicted_pressure: number;
  pressure_level: PressureLevel;
  confidence_score: number;
  key_driver: string;
  is_weekend: boolean;
  is_holiday: boolean;
}

export interface ForecastResponse {
  destination_id: string;
  destination_name: string;
  current_pressure: number;
  forecast_days: PressureDayForecast[];
  trend: 'RISING' | 'FALLING' | 'STABLE';
  summary: string;
}

export interface BeneficiaryDestination {
  destination_id: string;
  destination_name: string;
  redirected_visitors: number;
  estimated_revenue_gain_inr: number;
  capacity_remaining_percent: number;
}

export interface InterventionSimulationResult {
  destination_id: string;
  destination_name: string;
  intervention_type: string;
  intensity_percent: number;
  original_pressure: number;
  simulated_pressure: number;
  pressure_reduction_percent: number;
  redirected_tourists_count: number;
  beneficiary_destinations: BeneficiaryDestination[];
  total_rural_revenue_generated_inr: number;
  policy_summary: string;
  is_simulation: boolean;
  simulation_notes: string;
}

export interface DestinationPressureOverview {
  destination_id: string;
  destination_name: string;
  state: string;
  pressure_score: number;
  pressure_level: PressureLevel;
  confidence_score: number;
  occupancy_percent: number;
  active_events_count: number;
  traffic_status: string;
  is_chokepoint: boolean;
}

export interface FlowDistributionSummary {
  origin_destination_id: string;
  origin_destination_name: string;
  origin_pressure_score: number;
  redirected_travelers_7d: number;
  dispersal_efficiency_percent: number;
  top_absorber_id: string;
  top_absorber_name: string;
  economic_impact_inr_7d: number;
}

export interface CommandCenterData {
  total_destinations_monitored: number;
  critical_pressure_count: number;
  high_pressure_count: number;
  moderate_pressure_count: number;
  low_pressure_count: number;
  total_active_signals: number;
  average_data_confidence: number;
  destinations: DestinationPressureOverview[];
  flow_summary: FlowDistributionSummary[];
  system_status: string;
  last_updated: string;
}

// Milestone 5: Trust Layer & Observation Evidence Types
export type ProviderMode = 'MOCK' | 'REAL' | 'CACHED';
export type DataQuality = 'HIGH' | 'MEDIUM' | 'LOW' | 'DEGRADED';

// Raw observation within a signal's evidence block
export interface RawObservation {
  source_label: string;
  raw_value: number | string | null;
  is_mock: boolean;
  is_cached: boolean;
  age_seconds?: number;
}

// Per-signal evidence (used by the Evidence Drawer)
export interface SignalEvidenceEntry {
  signal_key: string;
  signal_name: string;
  provider_id: string;
  value: number;
  confidence: number;
  fallback_used: boolean;
  raw_observations: RawObservation[];
}

// Top-level evidence payload from /pressure/{id}/evidence
export interface PressureEvidence {
  destination_id: string;
  destination_name: string;
  composite_pressure_score: number;
  composite_confidence_pct: number;
  signals_used: number;
  signals_total: number;
  evidence_timestamp: string;
  signal_evidences: SignalEvidenceEntry[];
  // Legacy / alternate shape fields (kept for fallback)
  pressure_score?: number;
  classification?: string;
  confidence_score?: number;
  data_quality?: DataQuality;
  signals_available?: number;
  re_normalized?: boolean;
  missing_signals?: string[];
  signals?: SignalEvidence[];
  generated_at?: string;
  audit_verdict?: string;
}

// Provider status from /admin/providers/status
export interface ProviderStatus {
  provider_id: string;
  provider_name: string;
  status: 'LIVE' | 'CACHED' | 'MOCK' | 'DEGRADED' | 'ERROR' | string;
  confidence: number;
  latency_ms?: number;
  last_updated?: string;
  notes?: string;
  // Legacy fields
  signal_type?: string;
  mode?: ProviderMode;
  weight_percent?: number;
  last_reading_time?: string;
  reliability_score?: number;
  is_live?: boolean;
}

// Forecast accuracy/performance from /pressure/{id}/forecast-performance
export interface ProviderContribution {
  provider_id: string;
  provider_name: string;
  error_contribution_pct: number;
}

export interface ForecastPerformance {
  mae: number;
  rmse: number;
  hit_rate_percent?: number;
  sample_count?: number;
  accuracy_grade?: 'A' | 'B' | 'C' | 'D' | 'F' | string;
  provider_contributions?: ProviderContribution[];
  // Legacy fields
  directional_accuracy_percent?: number;
  evaluations_count?: number;
  evaluated_destinations?: string[];
  sample_period?: string;
  last_evaluated_at?: string;
}

export interface SignalEvidence {
  name: string;
  signal_type: string;
  raw_value: number;
  unit: string;
  normalized_value: number;
  weight: number;
  weighted_contribution: number;
  source: string;
  provider_mode: ProviderMode;
  confidence: number;
  data_quality: DataQuality;
  timestamp: string;
  notes?: string;
}

// ─── Milestone 6A: Historical Dataset & Baseline Evaluation ─────────────────

export interface DataQualityCheckResult {
  name: string;
  passed: boolean;
  detail: string;
  anomalies_detected: number;
}

export interface DataQualityReport {
  dataset_mode: 'SYNTHETIC DEMO' | 'REAL' | 'MIXED' | string;
  total_records: number;
  destinations_count: number;
  date_range: {
    start: string;
    end: string;
    days_covered?: string;
  };
  completeness_score: number;
  quality_rating: 'HIGH' | 'MEDIUM' | 'LOW' | 'DEGRADED';
  checks: DataQualityCheckResult[];
  is_valid: boolean;
  summary: string;
  evaluated_at?: string;
}

export interface ChronologicalSplitMetrics {
  split_name: string;
  start_date: string;
  end_date: string;
  sample_count: number;
  mae: number;
  rmse: number;
  directional_accuracy: number;
}

export interface DestinationErrorMetrics {
  destination_id: string;
  destination_name: string;
  sample_count: number;
  mae: number;
  rmse: number;
  directional_accuracy: number;
}

export interface SeasonErrorMetrics {
  season_name: string;
  period_label: string;
  sample_count: number;
  mae: number;
  rmse: number;
  directional_accuracy: number;
}

export interface DataSufficiencyVerdict {
  is_sufficient: boolean;
  confidence: string;
  sample_size_adequate: boolean;
  seasonality_represented: boolean;
  signal_coverage_complete: boolean;
  recommendation: string;
  rationale: string;
}

export interface BaselineEvaluationReport {
  dataset_size: number;
  date_range: {
    start: string;
    end: string;
  };
  destinations: string[];
  dataset_mode: 'SYNTHETIC DEMO' | 'REAL' | 'MIXED' | string;
  baseline_model_name: string;
  overall_mae: number;
  overall_rmse: number;
  directional_accuracy: number;
  split_metrics: ChronologicalSplitMetrics[];
  error_by_destination: DestinationErrorMetrics[];
  error_by_season: SeasonErrorMetrics[];
  data_sufficiency_verdict: DataSufficiencyVerdict;
  evaluated_at?: string;
}

export interface MLModelMetrics {
  test_mae?: number;
  test_rmse?: number;
  test_directional_accuracy?: number;
  val_mae?: number;
  val_rmse?: number;
}

export interface MLModelStatus {
  model_available: boolean;
  model_name: string;
  model_version: string;
  backend: string;
  training_dataset: string;
  dataset_mode: 'REAL' | 'SYNTHETIC' | 'MIXED' | 'NOT_TRAINED' | string;
  is_trained: boolean;
  last_trained?: string | null;
  metrics?: MLModelMetrics | null;
  baseline_model: string;
  fallback_active: boolean;
  synthetic_data_warning?: string | null;
}

export interface FeatureImportanceItem {
  feature: string;
  importance: number;
  rank: number;
}

export interface FeatureImportanceResponse {
  model_name: string;
  model_version: string;
  backend: string;
  dataset_mode: string;
  features: FeatureImportanceItem[];
  total_features: number;
  note: string;
}

export interface MLForecastDay {
  date: string;
  day_name: string;
  predicted_pressure: number;
  pressure_level: string;
  model_used: string;
  confidence: number;
  confidence_note: string;
  fallback_reason?: string | null;
  is_weekend: boolean;
}

export interface MLForecastResponse {
  destination_id: string;
  destination_name: string;
  horizon_days: number;
  current_pressure: number;
  forecast: MLForecastDay[];
  model_used: string;
  model_version: string;
  dataset_mode?: string | null;
  fallback_active: boolean;
  confidence_note: string;
  generated_at: string;
}

export interface MLTrainResponse {
  status: string;
  model_name: string;
  model_version: string;
  backend: string;
  dataset_mode: string;
  dataset_size: number;
  splits: Record<string, number>;
  metrics: {
    test_mae: number;
    test_rmse: number;
    test_directional_accuracy: number;
    val_mae: number;
    val_rmse: number;
  };
  baseline_test_metrics: {
    mae: number;
    rmse: number;
    directional_accuracy: number;
  };
  improvement_over_baseline: {
    mae_diff: number;
    rmse_diff: number;
    directional_accuracy_diff: number;
    ml_improves_mae: boolean;
    ml_improves_rmse: boolean;
  };
  feature_importances: Record<string, number>;
  synthetic_data_warning?: string;
}

export interface DemandCapacityStatus {
  destination_id: string;
  total_homestay_rooms: number;
  rooms_available: number;
  rooms_booked: number;
  capacity_available: number;
  capacity_pressure: number;
  capacity_threshold: number;
  absorber_status: string;
  is_constrained: boolean;
}

export interface TouristSignals {
  demand_trend_label: string;
  booking_pressure_label: string;
  recommendation_label?: string | null;
  is_alternative_advised: boolean;
}

export interface DemandMetrics {
  destination_id: string;
  destination_name: string;
  search_count_24h: number;
  search_count_7d: number;
  booking_count_24h: number;
  booking_count_7d: number;
  booking_conversion: number;
  availability_pressure: number;
  alternative_acceptance_rate: number;
  trend_percent: number;
  trend_direction: 'RISING' | 'DECLINING' | 'STABLE';
  normalized_search_demand: number;
  normalized_booking_demand: number;
  source: string;
  provider_mode: 'REAL' | 'SYNTHETIC' | 'MIXED' | string;
  confidence: number;
  data_quality: string;
  provenance_label: 'REAL — YATRI SETU NETWORK' | 'SYNTHETIC DEMO DATA' | 'MIXED — YATRI SETU NETWORK + SYNTHETIC DEMO' | string;
  is_leading_indicator: boolean;
  tourist_signals: TouristSignals;
  capacity: DemandCapacityStatus;
  last_updated: string;
  notes: string;
}

export interface CircuitDemandSummary {
  total_searches_24h: number;
  total_searches_7d: number;
  total_bookings_24h: number;
  total_bookings_7d: number;
  overall_booking_conversion: number;
  highest_demand_hub: string;
  primary_rural_absorber: string;
  source: string;
  provider_mode: string;
  provenance_label: string;
}

export interface CircuitDemandResponse {
  circuit_id: string;
  circuit_name: string;
  summary: CircuitDemandSummary;
  destinations: Record<string, DemandMetrics>;
  generated_at: string;
}

export interface AdminDemandOverview {
  total_events_recorded: number;
  events_24h_count: number;
  events_7d_count: number;
  event_breakdown: Record<string, number>;
  conversion_funnel: {
    searches: number;
    destination_selections: number;
    alternative_suggestions: number;
    alternative_acceptances: number;
    bookings: number;
    trips_started: number;
  };
  circuit_summary: CircuitDemandSummary;
  provenance_audit: {
    first_party_provider: string;
    mode: string;
    provenance_label: string;
    status: string;
    real_events_count?: number;
    synthetic_events_count?: number;
    signals_monitored: string[];
    synthetic_comparison: string;
  };
  recent_events_preview: Array<{
    id: string;
    destination_id?: string | null;
    event_type: string;
    timestamp: string;
    source: string;
    provenance: string;
  }>;
  last_updated: string;
}

// Milestone 7C: Live Weather + Traffic Intelligence & Pressure Recalculation

export interface WeatherObservation {
  destination_id: string;
  destination_name: string;
  observed_at: string;
  forecast_for?: string | null;
  temperature_c: number;
  temp_min_c: number;
  temp_max_c: number;
  precipitation_probability: number;
  precipitation_mm: number;
  humidity: number;
  wind_speed_kmh: number;
  weather_condition: string;
  severe_weather?: string | null;
  visibility_km: number;
  advisory: string;
  best_hours_for_outdoors?: string | null;
  source: string;
  provider_mode: 'REAL' | 'DEMO' | 'UNAVAILABLE' | string;
  confidence: number;
  data_quality: string;
  fetched_at: string;
  cache_status: 'LIVE' | 'CACHED' | 'STALE' | 'UNAVAILABLE' | string;
  expires_at?: string | null;
}

export interface RouteTrafficObservation {
  route_id: string;
  route_name: string;
  origin: string;
  destination_id: string;
  current_travel_time_min: number;
  historical_travel_time_min: number;
  travel_time_ratio: number;
  travel_time_anomaly_percent: number;
  congestion_level: 'NORMAL' | 'ELEVATED' | 'HIGH' | 'CRITICAL' | string;
  road_status: 'CLEAR' | 'SLOW' | 'RESTRICTED' | 'CLOSED' | string;
  incident_count: number;
  incident_description?: string | null;
}

export interface DestinationTrafficSummary {
  destination_id: string;
  destination_name: string;
  overall_congestion_score: number;
  average_travel_time_ratio: number;
  travel_time_anomaly_percent: number;
  incident_count: number;
  access_status: 'OPEN' | 'CAUTION' | 'DISRUPTED' | 'UNKNOWN' | string;
  primary_bottleneck_route?: string | null;
  critical_routes: RouteTrafficObservation[];
  observed_at: string;
  source: string;
  provider_mode: 'REAL' | 'DEMO' | 'UNAVAILABLE' | string;
  confidence: number;
  data_quality: string;
  fetched_at: string;
  cache_status: 'LIVE' | 'CACHED' | 'STALE' | 'UNAVAILABLE' | string;
  expires_at?: string | null;
}

export interface WeatherImpactSignal {
  destination_id: string;
  weather_impact: number;
  impact_factor: number;
  advisory_level: 'NORMAL' | 'ADVISORY' | 'WARNING' | 'CRITICAL' | string;
  tourism_suitability: 'EXCELLENT' | 'GOOD' | 'MODERATE' | 'POOR' | 'HAZARDOUS' | string;
  description: string;
  confidence: number;
  source: string;
  provider_mode: string;
  observed_at: string;
}

export interface TrafficImpactSignal {
  destination_id: string;
  traffic_impact_score: number;
  traffic_status: 'NORMAL' | 'ELEVATED' | 'HIGH' | 'CRITICAL' | string;
  travel_time_anomaly_percent: number;
  access_status: 'OPEN' | 'CAUTION' | 'DISRUPTED' | 'UNKNOWN' | string;
  bottleneck_corridor?: string | null;
  impact_description: string;
  confidence: number;
  source: string;
  provider_mode: string;
  observed_at: string;
}

export interface PressureDriver {
  signal: string;
  impact: number;
  description: string;
}

export interface PressureExplanation {
  destination_id: string;
  pressure_level: string;
  pressure_score: number;
  top_drivers: PressureDriver[];
  access_status: string;
  generated_at: string;
}

export interface PressureChangeDriver {
  signal: string;
  delta: number;
  description: string;
}

export interface PressureChangeSummary {
  destination_id: string;
  pressure_delta: number;
  previous_score: number;
  current_score: number;
  drivers: PressureChangeDriver[];
  previous_refresh_at?: string | null;
  current_refresh_at: string;
}

export interface DestinationLiveConditions {
  destination_id: string;
  destination_name: string;
  condition_type: string;
  pressure_score: number;
  pressure_level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL' | string;
  access_status: 'OPEN' | 'CAUTION' | 'DISRUPTED' | 'UNKNOWN' | string;
  weather: WeatherObservation;
  traffic: DestinationTrafficSummary;
  weather_impact: WeatherImpactSignal;
  traffic_impact: TrafficImpactSignal;
  event_pressure: number;
  holiday_pressure: number;
  first_party_demand: number;
  top_drivers: PressureDriver[];
  pressure_change?: PressureChangeSummary | null;
  provenance: string;
  data_quality: string;
  refreshed_at: string;
}

export type CircuitConditionsResponse = Record<string, DestinationLiveConditions>;

