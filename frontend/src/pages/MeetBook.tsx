import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

interface TherapistItem {
  id: number
  username: string
  first_name: string
  last_name: string
}

interface PatientItem {
  id: number
  username: string
  first_name: string
  last_name: string
}

interface Slot {
  id: number
  label: string
}

interface ScheduleConfig {
  rate: number
  interval: number
  max_number: number
  slots: Slot[]
  timezones: string[]
}

export default function MeetBook() {
  const navigate = useNavigate()
  const [therapists, setTherapists] = useState<TherapistItem[]>([])
  const [patients, setPatients] = useState<PatientItem[]>([])
  const [config, setConfig] = useState<ScheduleConfig | null>(null)

  const [loading, setLoading] = useState(true)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [formError, setFormError] = useState<Record<string, string[]>>({})

  const [therapistId, setTherapistId] = useState("")
  const [patientId, setPatientId] = useState("")
  const [date, setDate] = useState("")
  const [availableSlots, setAvailableSlots] = useState<number[]>([])
  const [selectedSlot, setSelectedSlot] = useState<number | null>(null)

  useEffect(() => {
    Promise.all([
      fetch("/api/therapists/").then((r) => r.json()),
      fetch("/api/patients/").then((r) => r.json()),
      fetch("/api/schedule-config/").then((r) => r.json()),
    ])
      .then(([therapistsData, patientsData, configData]) => {
        setTherapists(therapistsData)
        setPatients(patientsData)
        setConfig(configData)
        setError(null)
      })
      .catch(() => setError("Error al cargar datos iniciales"))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!therapistId || !date) {
      setAvailableSlots([])
      setSelectedSlot(null)
      return
    }
    fetch(`/api/therapists/${therapistId}/availability/?date=${date}`)
      .then((r) => r.json())
      .then((data) => {
        setAvailableSlots(data.availible_meets || [])
        setSelectedSlot(null)
      })
      .catch(() => setError("Error al cargar disponibilidad"))
  }, [therapistId, date])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setFormError({})
    setSubmitLoading(true)
    if (!therapistId || !patientId || !date || selectedSlot === null) {
      setError("Completa terapeuta, paciente, fecha y horario.")
      setSubmitLoading(false)
      return
    }
    fetch("/api/meets/book/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        therapist_id: Number(therapistId),
        patient_id: Number(patientId),
        date,
        number: selectedSlot,
      }),
    })
      .then((r) => r.json().then((data) => ({ status: r.status, data })))
      .then(({ status, data }) => {
        if (status === 200 || status === 201) {
          navigate("/meets")
          return
        }
        if (status === 400 && typeof data === "object") {
          setFormError(data)
          setError(null)
        } else {
          setError(data.detail || "Error al reservar cita")
        }
      })
      .catch(() => setError("Error de conexión"))
      .finally(() => setSubmitLoading(false))
  }

  if (loading) return <p className="p-6 text-gray-600">Cargando…</p>
  if (error && !config) return <p className="p-6 text-red-600">{error}</p>
  if (!config) return null

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-semibold text-gray-800 mb-6">Reservar cita</h1>
      {error && <p className="mb-4 text-red-600 text-sm">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Terapeuta *</label>
            <select
              value={therapistId}
              onChange={(e) => setTherapistId(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
            >
              <option value="">Selecciona terapeuta</option>
              {therapists.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.first_name} {t.last_name} ({t.username})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Paciente *</label>
            <select
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
            >
              <option value="">Selecciona paciente</option>
              {patients.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.first_name} {p.last_name} ({p.username})
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Fecha *</label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Horario disponible *</label>
          {(!therapistId || !date) && (
            <p className="text-sm text-gray-500">Selecciona terapeuta y fecha para ver horarios.</p>
          )}
          {therapistId && date && availableSlots.length === 0 && (
            <p className="text-sm text-gray-500 mt-1">No hay horarios libres para ese día.</p>
          )}
          {availableSlots.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-2">
              {config.slots
                .filter((s) => availableSlots.includes(s.id))
                .map((s) => (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => setSelectedSlot(s.id)}
                    className={`px-3 py-1 text-xs rounded border ${
                      selectedSlot === s.id
                        ? "bg-blue-600 text-white border-blue-600"
                        : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
                    }`}
                  >
                    {s.label}
                  </button>
                ))}
            </div>
          )}
        </div>
        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={submitLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {submitLoading ? "Reservando…" : "Reservar"}
          </button>
          <button
            type="button"
            onClick={() => navigate("/meets")}
            className="px-4 py-2 border border-gray-300 rounded font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  )
}

