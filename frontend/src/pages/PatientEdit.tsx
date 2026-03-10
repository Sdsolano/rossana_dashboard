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

interface PatientDetail {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  is_active: boolean
  telephone: string
  timezone_verbose: string
  timezone_index: number
}

export default function PatientEdit() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [config, setConfig] = useState<ScheduleConfig | null>(null)
  const [patient, setPatient] = useState<PatientDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [formError, setFormError] = useState<Record<string, string[]>>({})

  const [username, setUsername] = useState("")
  const [first_name, setFirst_name] = useState("")
  const [last_name, setLast_name] = useState("")
  const [email, setEmail] = useState("")
  const [is_active, setIs_active] = useState(true)
  const [telephone, setTelephone] = useState("")
  const [countryCode, setCountryCode] = useState("")
  const [timezone_verbose, setTimezone_verbose] = useState("")

  useEffect(() => {
    if (!id) return
    Promise.all([
      fetch(`/api/patients/${id}/`).then((r) =>
        r.ok ? r.json() : Promise.reject(new Error("No encontrado")),
      ),
      fetch("/api/schedule-config/").then((r) => r.json()),
    ])
      .then(([patientData, configData]) => {
        setPatient(patientData)
        setConfig(configData)
        setUsername(patientData.username)
        setFirst_name(patientData.first_name ?? "")
        setLast_name(patientData.last_name ?? "")
        setEmail(patientData.email)
        setIs_active(patientData.is_active ?? true)
        setTelephone(patientData.telephone ?? "")
        const tz = patientData.timezone_verbose ?? ""
        setTimezone_verbose(tz)
        const found = configData.countries?.find((c: Country) =>
          c.timezones?.some((t: CountryTz) => t.value === tz),
        )
        setCountryCode(found?.code ?? "")
        setError(null)
      })
      .catch(() => setError("Error al cargar"))
      .finally(() => setLoading(false))
  }, [id])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!id) return
    setFormError({})
    setSubmitLoading(true)
    fetch(`/api/patients/${id}/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username,
        first_name,
        last_name,
        email,
        is_active,
        telephone,
        timezone_verbose: timezone_verbose || undefined,
      }),
    })
      .then((r) => r.json().then((data) => ({ status: r.status, data })))
      .then(({ status, data }) => {
        if (status === 200) {
          navigate("/patients")
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
  if (!config || !patient) return null

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-semibold text-gray-800 mb-6">Editar paciente</h1>
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
            <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
            <input
              type="text"
              value={telephone}
              onChange={(e) => setTelephone(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
            />
          </div>
          <div className="flex items-center gap-2 mt-6 sm:mt-0">
            <input
              type="checkbox"
              id="is_active"
              checked={is_active}
              onChange={(e) => setIs_active(e.target.checked)}
              className="rounded"
            />
            <label htmlFor="is_active" className="text-sm font-medium text-gray-700">
              Activo
            </label>
          </div>
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
                <option key={c.code} value={c.code}>
                  {c.name}
                </option>
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
                  <option key={tz.value} value={tz.value}>
                    {tz.label}
                  </option>
                ))}
            </select>
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
          <button
            type="button"
            onClick={() => navigate("/patients")}
            className="px-4 py-2 border border-gray-300 rounded font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  )
}

