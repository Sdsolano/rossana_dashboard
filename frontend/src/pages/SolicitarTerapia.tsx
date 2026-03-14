import { useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"

interface TherapistItem {
  id: number
  username: string
  first_name: string
  last_name: string
}

interface SlotOption {
  therapist_id: number
  therapist_name: string
  number: number
  label: string
}

interface ScheduleConfig {
  rate: number
  interval: number
  max_number: number
  slots: { id: number; label: string }[]
  timezones: string[]
  countries?: { code: string; name: string; timezones: { value: string; label: string }[] }[]
}

const STEP_1 = 1
const STEP_2 = 2

const WEEKDAY_NAMES = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
const MONTH_NAMES = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

/** Días siguientes a partir de hoy para elegir */
function buildDayOptions(count: number): { date: string; weekday: string; day: number; month: string; monthYear: string }[] {
  const out: { date: string; weekday: string; day: number; month: string; monthYear: string }[] = []
  const today = new Date()
  for (let i = 0; i < count; i++) {
    const d = new Date(today)
    d.setDate(today.getDate() + i)
    const y = d.getFullYear()
    const m = d.getMonth() + 1
    const day = d.getDate()
    const dateStr = `${y}-${String(m).padStart(2, "0")}-${String(day).padStart(2, "0")}`
    out.push({
      date: dateStr,
      weekday: WEEKDAY_NAMES[d.getDay()],
      day,
      month: MONTH_NAMES[m],
      monthYear: `${MONTH_NAMES[m]} ${y}`,
    })
  }
  return out
}

/** Formatea fecha para resumen: "16 de marzo, 2026" */
function formatDateLong(dateStr: string): string {
  const [y, m, d] = dateStr.split("-").map(Number)
  return `${d} de ${MONTH_NAMES[m].toLowerCase()}, ${y}`
}

function Logo() {
  return (
    <div className="flex items-center gap-2">
      <svg
        className="h-9 w-9 text-violet-600"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <circle cx="12" cy="12" r="10" />
        <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
        <path d="m14 10 4-4 2 2-4 4" strokeWidth="1.5" />
      </svg>
      <div className="leading-tight">
        <span className="block text-[10px] sm:text-xs font-medium text-gray-500 uppercase tracking-wider">Sistema</span>
        <span className="block text-base sm:text-lg font-bold text-gray-900 tracking-tight">QMM Team</span>
      </div>
    </div>
  )
}

/** Lista plana de zonas horarias desde countries (IANA) para el select */
function flattenTimezones(config: ScheduleConfig): { value: string; label: string }[] {
  const list: { value: string; label: string }[] = []
  if (!config.countries?.length) {
    return (config.timezones || []).map((tz) => ({ value: tz, label: tz }))
  }
  for (const c of config.countries) {
    for (const tz of c.timezones || []) {
      list.push({ value: tz.value, label: `${c.name} — ${tz.label}` })
    }
  }
  return list
}

export default function SolicitarTerapia() {
  const navigate = useNavigate()
  const [step, setStep] = useState(STEP_1)
  const [config, setConfig] = useState<ScheduleConfig | null>(null)
  const [therapists, setTherapists] = useState<TherapistItem[]>([])
  const [loading, setLoading] = useState(true)
  const [slotsLoading, setSlotsLoading] = useState(false)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [formError, setFormError] = useState<Record<string, string[]>>({})

  const [date, setDate] = useState("")
  const [timezone, setTimezone] = useState("")
  const [therapistId, setTherapistId] = useState<string>("")
  const [slots, setSlots] = useState<SlotOption[]>([])
  const [selectedSlot, setSelectedSlot] = useState<SlotOption | null>(null)

  const [first_name, setFirst_name] = useState("")
  const [last_name, setLast_name] = useState("")
  const [email, setEmail] = useState("")
  const [telephone, setTelephone] = useState("")

  const dayOptions = buildDayOptions(14)
  const selectedDayInfo = dayOptions.find((d) => d.date === date)
  const timezoneOptions = config ? flattenTimezones(config) : []

  useEffect(() => {
    Promise.all([
      fetch("/api/schedule-config/").then((r) => r.json()),
      fetch("/api/therapists/").then((r) => r.json()),
    ])
      .then(([configData, therapistsData]) => {
        setConfig(configData)
        setTherapists(therapistsData)
        const tzList = flattenTimezones(configData)
        if (tzList.length && !timezone) {
          const preferred = tzList.find((z) => z.value.includes("Buenos_Aires")) ?? tzList[0]
          setTimezone(preferred.value)
        }
        setError(null)
      })
      .catch(() => setError("Error al cargar datos"))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!date) {
      setSlots([])
      setSelectedSlot(null)
      return
    }
    setSlotsLoading(true)
    setSelectedSlot(null)
    setError(null)
    const params = new URLSearchParams({ date })
    if (therapistId) params.set("therapist_id", therapistId)
    const tzValue = (timezone || "UTC").trim()
    if (tzValue) params.set("timezone_verbose", tzValue)
    fetch(`/api/availability/?${params}`)
      .then(async (r) => {
        const data = await r.json().catch(() => ({}))
        if (!r.ok) {
          throw new Error(typeof data?.detail === "string" ? data.detail : "Error al cargar horarios")
        }
        return data
      })
      .then((data) => {
        setSlots(data.slots || [])
        setError(null)
      })
      .catch((err) => {
        const msg = err instanceof Error ? err.message : ""
        const isNetwork = /failed to fetch|network|connection/i.test(msg)
        setError(isNetwork ? "No se pudo conectar al servidor. Revisá que el backend esté corriendo (puerto 8000)." : (msg || "Error al cargar horarios"))
      })
      .finally(() => setSlotsLoading(false))
  }, [date, therapistId, timezone])

  const canGoNext = date && selectedSlot
  const handleStep1Next = (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    if (!canGoNext) {
      setError("Seleccioná un día y un horario.")
      return
    }
    setStep(STEP_2)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setFormError({})
    setError(null)
    if (!selectedSlot || !first_name.trim() || !last_name.trim() || !email.trim()) {
      setError("Completá nombre, apellido y email.")
      return
    }
    setSubmitLoading(true)
    fetch("/api/meets/solicitar/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        therapist_id: selectedSlot.therapist_id,
        date,
        number: selectedSlot.number,
        first_name: first_name.trim(),
        last_name: last_name.trim(),
        email: email.trim(),
        telephone: telephone.trim() || undefined,
        timezone_verbose: timezone || undefined,
      }),
    })
      .then((r) => r.json().then((data) => ({ status: r.status, data })))
      .then(({ status, data }) => {
        if (status === 200) {
          navigate("/solicitud-enviada", { state: { meet: data } })
          return
        }
        if (status === 400 && typeof data === "object") setFormError(data)
        else setError(data.detail || "Error al reservar.")
      })
      .catch(() => setError("Error de conexión"))
      .finally(() => setSubmitLoading(false))
  }

  if (loading || !config) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <p className="text-gray-600">Cargando…</p>
      </div>
    )
  }

  const resumenPanel = (
    <aside className="bg-gray-50 border border-gray-100 rounded-2xl p-6 h-fit sticky top-24">
      <h2 className="text-lg font-bold text-gray-900 mb-4">Resumen de tu solicitud</h2>
      <dl className="space-y-3 text-sm">
        <div>
          <dt className="text-gray-500">Duración</dt>
          <dd className="font-medium text-gray-900">{config.rate} minutos</dd>
        </div>
        <div>
          <dt className="text-gray-500">Vía</dt>
          <dd className="font-medium text-gray-900">Zoom meeting</dd>
        </div>
        <div>
          <dt className="text-gray-500">Día</dt>
          <dd className="font-medium text-gray-900">
            {date ? formatDateLong(date) : "—"}
          </dd>
        </div>
        <div>
          <dt className="text-gray-500">Horario (24H)</dt>
          <dd className="font-medium text-gray-900">
            {selectedSlot ? selectedSlot.label : "—"}
          </dd>
        </div>
        <div>
          <dt className="text-gray-500">Valor</dt>
          <dd className="font-medium text-gray-900">A confirmar</dd>
        </div>
      </dl>
    </aside>
  )

  return (
    <div className="min-h-screen bg-white">
      {/* Header igual al landing */}
      <header className="sticky top-0 z-50 border-b border-gray-100 bg-white">
        <div className="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-4">
          <Link to="/" className="flex items-center gap-2">
            <Logo />
          </Link>
          <nav className="flex items-center gap-6 text-sm font-medium text-gray-600">
            <Link to="/" className="hover:text-gray-900">Inicio</Link>
            <a href="/#como-funciona" className="hover:text-gray-900">Cómo funciona</a>
            <a href="/#preguntas-frecuentes" className="hover:text-gray-900">Preguntas frecuentes</a>
            <span className="px-4 py-2 rounded-lg bg-violet-600 text-white font-semibold">Solicita tu terapia</span>
          </nav>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
          Solicita tu terapia QMM Team
        </h1>
        <p className="text-gray-600 mb-8 max-w-xl">
          {step === STEP_1
            ? "Seleccioná día y hora para tu terapia. Después completá tus datos y confirmá tu pedido. Es así de fácil."
            : "Completá tus datos para confirmar la reserva."}
        </p>

        {error && <p className="mb-4 text-red-600 text-sm">{error}</p>}

        {step === STEP_1 && (
          <form onSubmit={handleStep1Next} className="flex flex-col lg:flex-row gap-8">
            <div className="flex-1 space-y-6">
              {/* Terapeuta opcional */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Terapeuta (opcional)</label>
                <select
                  value={therapistId}
                  onChange={(e) => setTherapistId(e.target.value)}
                  className="w-full max-w-xs border border-gray-300 rounded-xl px-3 py-2.5 bg-white"
                >
                  <option value="">Cualquier terapeuta</option>
                  {therapists.map((t) => (
                    <option key={t.id} value={t.id}>{t.first_name} {t.last_name}</option>
                  ))}
                </select>
              </div>

              {/* Paso 1: Elegí el día */}
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-2">Paso 1: Elegí el día</h3>
                <p className="text-xs text-gray-500 mb-3">
                  {selectedDayInfo ? selectedDayInfo.monthYear : dayOptions[0]?.monthYear}
                </p>
                <div className="flex flex-wrap gap-2">
                  {dayOptions.map((d) => (
                    <button
                      key={d.date}
                      type="button"
                      onClick={() => setDate(d.date)}
                      className={`px-4 py-2.5 rounded-xl border text-sm font-medium transition ${
                        date === d.date
                          ? "bg-violet-600 text-white border-violet-600"
                          : "bg-white text-gray-700 border-gray-200 hover:bg-violet-50 hover:border-violet-200"
                      }`}
                    >
                      {d.weekday} {d.day}
                    </button>
                  ))}
                </div>
              </div>

              {/* Paso 2: Elegí la hora */}
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-2">Paso 2: Elegí la hora</h3>
                <div className="flex flex-wrap items-center gap-3 mb-3">
                  <span className="flex items-center gap-2 text-sm text-gray-600">
                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <circle cx="12" cy="12" r="10" strokeWidth="2" />
                      <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" strokeWidth="2" />
                    </svg>
                    Uso horario
                  </span>
                  <select
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                    className="border border-gray-300 rounded-xl px-3 py-2 text-sm min-w-[220px] bg-white"
                  >
                    {timezoneOptions.map((opt) => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
                {!date && <p className="text-sm text-gray-500">Elegí un día para ver horarios.</p>}
                {date && slotsLoading && <p className="text-sm text-gray-500">Cargando horarios…</p>}
                {date && !slotsLoading && slots.length === 0 && (
                  <p className="text-sm text-amber-600">
                    No hay turnos libres para esa fecha. Probá otro día.
                  </p>
                )}
                {slots.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {slots.map((s) => (
                      <button
                        key={`${s.therapist_id}-${s.number}`}
                        type="button"
                        onClick={() => setSelectedSlot(s)}
                        className={`px-3 py-2 text-sm rounded-xl border transition ${
                          selectedSlot?.therapist_id === s.therapist_id && selectedSlot?.number === s.number
                            ? "bg-violet-600 text-white border-violet-600"
                            : "bg-white text-gray-700 border-gray-200 hover:bg-violet-50 hover:border-violet-200"
                        }`}
                      >
                        {s.label}
                        {slots.filter((x) => x.label === s.label && x.therapist_id !== s.therapist_id).length > 0 && (
                          <span className="ml-1 opacity-80"> — {s.therapist_name}</span>
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="submit"
                  disabled={!canGoNext}
                  className="px-5 py-2.5 rounded-xl bg-violet-600 text-white font-semibold hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Solicita tu terapia (siguiente)
                </button>
                <Link
                  to="/"
                  className="px-5 py-2.5 rounded-xl border border-gray-300 font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </Link>
              </div>
            </div>
            <div className="lg:w-80 flex-shrink-0">{resumenPanel}</div>
          </form>
        )}

        {step === STEP_2 && (
          <form onSubmit={handleSubmit} className="flex flex-col lg:flex-row gap-8">
            <div className="flex-1 space-y-4">
              <div className="rounded-xl border border-violet-100 bg-violet-50/50 p-4">
                <p className="text-sm text-gray-700">
                  <strong>Reserva:</strong> {date && formatDateLong(date)} · {selectedSlot?.label} · {selectedSlot?.therapist_name}
                </p>
                <button
                  type="button"
                  onClick={() => setStep(STEP_1)}
                  className="mt-2 text-sm text-violet-600 hover:text-violet-800 font-medium"
                >
                  Cambiar fecha u horario
                </button>
              </div>
              <p className="text-sm font-medium text-gray-700">Datos del paciente</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-700 mb-1">Nombre *</label>
                  <input
                    type="text"
                    value={first_name}
                    onChange={(e) => setFirst_name(e.target.value)}
                    className="w-full border border-gray-300 rounded-xl px-3 py-2"
                    placeholder="Tu nombre"
                    required
                  />
                  {formError.first_name && <p className="mt-1 text-xs text-red-600">{formError.first_name[0]}</p>}
                </div>
                <div>
                  <label className="block text-sm text-gray-700 mb-1">Apellido *</label>
                  <input
                    type="text"
                    value={last_name}
                    onChange={(e) => setLast_name(e.target.value)}
                    className="w-full border border-gray-300 rounded-xl px-3 py-2"
                    placeholder="Tu apellido"
                    required
                  />
                  {formError.last_name && <p className="mt-1 text-xs text-red-600">{formError.last_name[0]}</p>}
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-700 mb-1">Correo electrónico *</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full border border-gray-300 rounded-xl px-3 py-2"
                  placeholder="tu@email.com"
                  required
                />
                <p className="mt-1 text-xs text-gray-500">Te enviamos la confirmación y el link de la sesión.</p>
                {formError.email && <p className="mt-1 text-xs text-red-600">{formError.email[0]}</p>}
              </div>
              <div>
                <label className="block text-sm text-gray-700 mb-1">Teléfono (opcional)</label>
                <input
                  type="tel"
                  value={telephone}
                  onChange={(e) => setTelephone(e.target.value)}
                  className="w-full border border-gray-300 rounded-xl px-3 py-2"
                  placeholder="+54 11 1234-5678"
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  disabled={submitLoading}
                  className="px-5 py-2.5 rounded-xl bg-violet-600 text-white font-semibold hover:bg-violet-700 disabled:opacity-50"
                >
                  {submitLoading ? "Reservando…" : "Confirmar reserva"}
                </button>
                <button
                  type="button"
                  onClick={() => setStep(STEP_1)}
                  className="px-5 py-2.5 rounded-xl border border-gray-300 font-medium text-gray-700 hover:bg-gray-50"
                >
                  Atrás
                </button>
              </div>
            </div>
            <div className="lg:w-80 flex-shrink-0">{resumenPanel}</div>
          </form>
        )}
      </div>
    </div>
  )
}
