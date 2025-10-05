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
  start: string // ISO 8601 string, e.g., "2025-10-26T10:00:00Z"
  end: string // ISO 8601 string
}

export interface AvailabilityResponse {
  date: string // YYYY-MM-DD
  busy_slots: BusySlot[]
}

export interface BookingPayload {
  room_id: number
  start_datetime: string // ISO 8601 string
  end_datetime: string // ISO 8601 string
  comment?: string
}
