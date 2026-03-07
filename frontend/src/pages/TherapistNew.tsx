import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

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
  countries: Country[]
}

const DAY_NAMES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

export default function TherapistNew() {
  const navigate = useNavigate()
  const [config, setConfig] = useState<ScheduleConfig | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [formError, setFormError] = useState<Record<string, string[]>>({})

  const [username, setUsername] = useState("")
  const [first_name, setFirst_name] = useState("")
  const [last_name, setLast_name] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [password_confirm, setPassword_confirm] = useState("")
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

  useEffect(() => {
    fetch("/api/schedule-config/")
      .then((res) => res.json())
      .then((data) => {
        setConfig(data)
        setError(null)
      })
      .catch(() => setError("Error al cargar configuración"))
      .finally(() => setLoading(false))
  }, [])

  const daySetters = [setMonday, setTuesday, setWednesday, setThursday, setFriday, setSaturday, setSunday]
  const dayValues = [monday, tuesday, wednesday, thursday, friday, saturday, sunday]

  const toggleSlot = (dayIndex: number, slotId: number) => {
    const setter = daySetters[dayIndex]
    const current = dayValues[dayIndex]
    if (current.includes(slotId)) {
      setter(current.filter((id) => id !== slotId))
    } else {
      setter([...current, slotId].sort((a, b) => a - b))
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setFormError({})
    setSubmitLoading(true)
    fetch("/api/therapists/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username,
        first_name,
        last_name,
        email,
        password,
        password_confirm,
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
        if (status === 201) {
          navigate("/therapists")
          return
        }
        if (status === 400 && typeof data === "object") setFormError(data)
        else setError("Error al crear terapeuta")
      })
      .catch(() => setError("Error de conexión"))
      .finally(() => setSubmitLoading(false))
  }

  if (loading) return <p className="p-6 text-gray-600">Cargando…</p>
  if (error) return <p className="p-6 text-red-600">{error}</p>
  if (!config) return null

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-semibold text-gray-800 mb-6">Agregar terapeuta</h1>
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
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña *</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
              required
            />
            {formError.password && <p className="text-red-600 text-sm mt-1">{formError.password[0]}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Repetir contraseña *</label>
            <input
              type="password"
              value={password_confirm}
              onChange={(e) => setPassword_confirm(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
              required
            />
            {formError.password_confirm && <p className="text-red-600 text-sm mt-1">{formError.password_confirm[0]}</p>}
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
                const firstTz = country?.timezones?.[0]?.value ?? ""
                setTimezone_verbose(firstTz)
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
          <p className="text-sm text-gray-600 mb-3">Selecciona los horarios en que el terapeuta está disponible (por día).</p>
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
            {submitLoading ? "Guardando…" : "Agregar terapeuta"}
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
