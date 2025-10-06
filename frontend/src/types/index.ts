export interface District {
  id: number
  name: string
}

export interface YouthCenter {
  id: number
  name: string
  district: District
  emblem: string | null
  address: string
  phone: string
}

export interface RoomTag {
  id: number
  name: string
}

export interface Room {
  id: number
  name: string
  description: string
  image: string | null
  capacity: number
  tags: RoomTag[]
  center: YouthCenter
  responsible_phone: string
}

export interface BusySlot {
  start: string
  end: string
}

export interface AvailabilityResponse {
  date: string // YYYY-MM-DD
  busy_slots: BusySlot[]
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface BookingPayload {
  room_id: number
  start_datetime: string
  end_datetime: string
  comment?: string
  applicant_phone?: string
  applicant_telegram_username?: string
}

export interface Booking {
  id: number
  room: Room
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'CANCELED'
  start_at: string // ISO date string
  end_at: string // ISO date string
  rejection_reason: string | null
  comment: string
  created_at: string
}