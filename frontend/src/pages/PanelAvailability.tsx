import { useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

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

export default function PanelAvailability() {
  const { token, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [config, setConfig] = useState<ScheduleConfig | null>(null)
  const [therapist, setTherapist] = useState<TherapistDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [formError, setFormError] = useState<Record<string, string[]>>({})

  const [countryCode, setCountryCode] = useState("")
  const [timezone_verbose, setTimezone_verbose] = useState("")
  const [monday, setMonday] = useState<number[]>([])
  const [tuesday, setTuesday] = useState<number[]>([])
  const [wednesday, setWednesday] = useState<number[]>([])
  const [thursday, setThursday] = useState<number[]>([])
  const [friday, setFriday] = useState<number[]>([])
  const [saturday, setSaturday] = useState<number[]>([])
  const [sunday, setSunday] = useState<number[]>([])


  useEffect(() => {
    if (!isAuthenticated || !token) {
      navigate("/login")
      return
    }
    const headers = { Authorization: `Token ${token}` }
    Promise.all([
      fetch("/api/me/availability/", { headers }).then((r) =>
        r.ok ? r.json() : Promise.reject(new Error("No autorizado"))
      ),
      fetch("/api/schedule-config/").then((r) => r.json()),
    ])
      .then(([meData, configData]) => {
        setTherapist(meData)
        setConfig(configData)
        const tz = meData.timezone_verbose ?? ""
        setTimezone_verbose(tz)
        const found = configData.countries?.find((c: Country) =>
          c.timezones?.some((t: CountryTz) => t.value === tz)
        )
        setCountryCode(found?.code ?? "")
        setMonday(meData.monday ?? [])
        setTuesday(meData.tuesday ?? [])
        setWednesday(meData.wednesday ?? [])
        setThursday(meData.thursday ?? [])
        setFriday(meData.friday ?? [])
        setSaturday(meData.saturday ?? [])
        setSunday(meData.sunday ?? [])
        setError(null)
      })
      .catch(() => setError("Error al cargar"))
      .finally(() => setLoading(false))
  }, [isAuthenticated, token, navigate])

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
    setFormError({})
    setSubmitLoading(true)
    fetch("/api/me/availability/", {
      method: "PUT",
      headers: token ? { Authorization: `Token ${token}`, "Content-Type": "application/json" } : { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: therapist?.username,
        first_name: therapist?.first_name,
        last_name: therapist?.last_name,
        email: therapist?.email,
        is_active: therapist?.is_active ?? true,
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
      .then((r) => r.json().then((data) => ({ status: r.status, data })))
      .then(({ status, data }) => {
        if (status === 200) {
          navigate("/panel")
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
      <div className="flex items-center gap-4 mb-6">
        <Link to="/panel" className="text-gray-600 hover:text-gray-900 font-medium">
          ← Panel
        </Link>
        <h1 className="text-2xl font-semibold text-gray-800">Mi disponibilidad</h1>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4">
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
        <div className="border-t pt-4">
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
        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={submitLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {submitLoading ? "Guardando…" : "Guardar"}
          </button>
          <Link
            to="/panel"
            className="px-4 py-2 border border-gray-300 rounded font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancelar
          </Link>
        </div>
      </form>
    </div>
  )
}
