import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"

interface CountryTz {
  value: string
  label: string
}
interface Country {
  code: string
  name: string
  timezones: CountryTz[]
}
interface ScheduleConfig {
  rate: number
  interval: number
  max_number: number
  slots: { id: number; label: string }[]
  timezones: string[]
  countries?: Country[]
}

interface TherapistDetail {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  is_active: boolean
  timezone_verbose: string
  monday: number[]
  tuesday: number[]
  wednesday: number[]
  thursday: number[]
  friday: number[]
  saturday: number[]
  sunday: number[]
}

const DAY_NAMES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

export default function TherapistEdit() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [config, setConfig] = useState<ScheduleConfig | null>(null)
  const [therapist, setTherapist] = useState<TherapistDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [formError, setFormError] = useState<Record<string, string[]>>({})

  const [username, setUsername] = useState("")
  const [first_name, setFirst_name] = useState("")
  const [last_name, setLast_name] = useState("")
  const [email, setEmail] = useState("")
  const [is_active, setIs_active] = useState(true)
  const [countryCode, setCountryCode] = useState("")
  const [timezone_verbose, setTimezone_verbose] = useState("")
  const [monday, setMonday] = useState<number[]>([])
  const [tuesday, setTuesday] = useState<number[]>([])
  const [wednesday, setWednesday] = useState<number[]>([])
  const [thursday, setThursday] = useState<number[]>([])
  const [friday, setFriday] = useState<number[]>([])
  const [saturday, setSaturday] = useState<number[]>([])
  const [sunday, setSunday] = useState<number[]>([])
  const [freedays, setFreedays] = useState<string[]>([])
  const [newFreedayDate, setNewFreedayDate] = useState("")

  const loadFreedays = () => {
    if (!id) return
    const today = new Date()
    const to = new Date(today)
    to.setDate(to.getDate() + 60)
    const fromStr = today.toISOString().slice(0, 10)
    const toStr = to.toISOString().slice(0, 10)
    fetch(`/api/therapists/${id}/freedays/?from=${fromStr}&to=${toStr}`)
      .then((r) => r.json())
      .then((d) => setFreedays(d.dates || []))
      .catch(() => {})
  }

  useEffect(() => {
    if (!id) return
    Promise.all([
      fetch(`/api/therapists/${id}/`).then((r) => (r.ok ? r.json() : Promise.reject(new Error("No encontrado")))),
      fetch("/api/schedule-config/").then((r) => r.json()),
    ])
      .then(([therapistData, configData]) => {
        setTherapist(therapistData)
        setConfig(configData)
        setUsername(therapistData.username)
        setFirst_name(therapistData.first_name ?? "")
        setLast_name(therapistData.last_name ?? "")
        setEmail(therapistData.email)
        setIs_active(therapistData.is_active ?? true)
        const tz = therapistData.timezone_verbose ?? ""
        setTimezone_verbose(tz)
        const found = configData.countries?.find((c: Country) =>
          c.timezones?.some((t: CountryTz) => t.value === tz)
        )
        setCountryCode(found?.code ?? "")
        setMonday(therapistData.monday ?? [])
        setTuesday(therapistData.tuesday ?? [])
        setWednesday(therapistData.wednesday ?? [])
        setThursday(therapistData.thursday ?? [])
        setFriday(therapistData.friday ?? [])
        setSaturday(therapistData.saturday ?? [])
        setSunday(therapistData.sunday ?? [])
        setError(null)
        loadFreedays()
      })
      .catch(() => setError("Error al cargar terapeuta"))
      .finally(() => setLoading(false))
  }, [id])

  const daySetters = [setMonday, setTuesday, setWednesday, setThursday, setFriday, setSaturday, setSunday]
  const dayValues = [monday, tuesday, wednesday, thursday, friday, saturday, sunday]

  const toggleSlot = (dayIndex: number, slotId: number) => {
    const setter = daySetters[dayIndex]
    const current = dayValues[dayIndex]
    if (current.includes(slotId)) {
      setter(current.filter((i) => i !== slotId))
    } else {
      setter([...current, slotId].sort((a, b) => a - b))
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!id) return
    setFormError({})
    setSubmitLoading(true)
    fetch(`/api/therapists/${id}/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username,
        first_name,
        last_name,
        email,
        is_active,
        timezone_verbose: timezone_verbose || undefined,
        monday,
        tuesday,
        wednesday,
        thursday,
        friday,
        saturday,
        sunday,
      }),
    })
      .then((res) => res.json().then((data) => ({ status: res.status, data })))
      .then(({ status, data }) => {
        if (status === 200) {
          navigate("/therapists")
          return
        }
        if (status === 400 && typeof data === "object") setFormError(data)
        else setError("Error al guardar")
      })
      .catch(() => setError("Error de conexión"))
      .finally(() => setSubmitLoading(false))
  }

  if (loading) return <p className="p-6 text-gray-600">Cargando…</p>
  if (error) return <p className="p-6 text-red-600">{error}</p>
  if (!config || !therapist) return null

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-semibold text-gray-800 mb-6">Editar terapeuta</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Usuario *</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
              required
            />
            {formError.username && <p className="text-red-600 text-sm mt-1">{formError.username[0]}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
              required
            />
            {formError.email && <p className="text-red-600 text-sm mt-1">{formError.email[0]}</p>}
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
            <input
              type="text"
              value={first_name}
              onChange={(e) => setFirst_name(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Apellido</label>
            <input
              type="text"
              value={last_name}
              onChange={(e) => setLast_name(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
            />
          </div>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="is_active"
            checked={is_active}
            onChange={(e) => setIs_active(e.target.checked)}
            className="rounded"
          />
          <label htmlFor="is_active" className="text-sm font-medium text-gray-700">Activo</label>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">País</label>
            <select
              value={countryCode}
              onChange={(e) => {
                const code = e.target.value
                setCountryCode(code)
                const country = config.countries?.find((c) => c.code === code)
                setTimezone_verbose(country?.timezones?.[0]?.value ?? "")
              }}
              className="w-full border border-gray-300 rounded px-3 py-2"
            >
              <option value="">Seleccione país</option>
              {config.countries?.map((c) => (
                <option key={c.code} value={c.code}>{c.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Zona horaria</label>
            <select
              value={timezone_verbose}
              onChange={(e) => setTimezone_verbose(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
              disabled={!countryCode}
            >
              <option value="">Seleccione zona horaria</option>
              {config.countries
                ?.find((c) => c.code === countryCode)
                ?.timezones?.map((tz) => (
                  <option key={tz.value} value={tz.value}>{tz.label}</option>
                ))}
            </select>
          </div>
        </div>

        <div className="border-t pt-4 mt-6">
          <h2 className="text-lg font-medium text-gray-800 mb-3">Disponibilidad semanal</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {DAY_NAMES.map((name, dayIndex) => (
              <div key={name} className="border rounded p-3 bg-gray-50">
                <div className="font-medium text-gray-700 mb-2">{name}</div>
                <div className="flex flex-wrap gap-1 max-h-32 overflow-y-auto">
                  {config.slots.map((slot) => (
                    <button
                      key={slot.id}
                      type="button"
                      onClick={() => toggleSlot(dayIndex, slot.id)}
                      className={`text-xs px-2 py-1 rounded ${
                        dayValues[dayIndex].includes(slot.id)
                          ? "bg-blue-600 text-white"
                          : "bg-white border border-gray-300 text-gray-700 hover:bg-gray-100"
                      }`}
                    >
                      {slot.label.slice(0, 5)}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="border-t pt-4 mt-6">
          <h2 className="text-lg font-medium text-gray-800 mb-3">Días bloqueados (no atiende)</h2>
          <p className="text-sm text-gray-600 mb-2">Estos días el terapeuta no tiene disponibilidad.</p>
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <input
              type="date"
              value={newFreedayDate}
              onChange={(e) => setNewFreedayDate(e.target.value)}
              className="border border-gray-300 rounded px-3 py-2"
            />
            <button
              type="button"
              onClick={() => {
                if (!newFreedayDate || !id) return
                fetch(`/api/therapists/${id}/freedays/`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ date: newFreedayDate }),
                })
                  .then((r) => r.json())
                  .then(() => {
                    setFreedays((prev) => (prev.includes(newFreedayDate) ? prev : [...prev, newFreedayDate].sort()))
                    setNewFreedayDate("")
                  })
              }}
              className="px-3 py-2 bg-amber-100 text-amber-800 rounded font-medium hover:bg-amber-200"
            >
              Bloquear día
            </button>
          </div>
          <ul className="space-y-1">
            {freedays.length === 0 ? (
              <li className="text-sm text-gray-500">Ningún día bloqueado en los próximos 60 días.</li>
            ) : (
              freedays.map((d) => (
                <li key={d} className="flex items-center justify-between py-1 border-b border-gray-100">
                  <span className="text-sm">{d}</span>
                  <button
                    type="button"
                    onClick={() => {
                      if (!id) return
                      fetch(`/api/therapists/${id}/freedays/?date=${d}`, { method: "DELETE" }).then(() =>
                        setFreedays((prev) => prev.filter((x) => x !== d))
                      )
                    }}
                    className="text-red-600 hover:underline text-sm"
                  >
                    Desbloquear
                  </button>
                </li>
              ))
            )}
          </ul>
        </div>

        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={submitLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {submitLoading ? "Guardando…" : "Guardar"}
          </button>
          <button
            type="button"
            onClick={() => navigate("/therapists")}
            className="px-4 py-2 border border-gray-300 rounded font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  )
}
