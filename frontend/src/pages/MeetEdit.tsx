import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"

interface MeetDetail {
  id: number
  therapist_id: number
  patient_id: number | null
  patient_name: string
  date: string
  number: number
  status: string
}

const STATUS_OPTIONS: { value: string; label: string }[] = [
  { value: "F", label: "Libre" },
  { value: "T", label: "Temporal" },
  { value: "U", label: "Pago pendiente" },
  { value: "D", label: "Confirmado" },
  { value: "R", label: "Reprogramado" },
  { value: "C", label: "Cancelado" },
  { value: "P", label: "Presente" },
  { value: "A", label: "Ausente" },
]

export default function MeetEdit() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [meet, setMeet] = useState<MeetDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [formError, setFormError] = useState<Record<string, string[]>>({})

  const [status, setStatus] = useState("F")
  const [patientIdInput, setPatientIdInput] = useState("")

  useEffect(() => {
    if (!id) return
    setLoading(true)
    fetch(`/api/meets/${id}/`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error("No encontrado"))))
      .then((data: MeetDetail) => {
        setMeet(data)
        setStatus(data.status)
        setPatientIdInput(data.patient_id ? String(data.patient_id) : "")
        setError(null)
      })
      .catch(() => setError("Error al cargar cita"))
      .finally(() => setLoading(false))
  }, [id])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!id) return
    setFormError({})
    setSubmitLoading(true)
    const body: any = {
      status,
    }
    if (patientIdInput.trim() === "") {
      body.patient_id = null
    } else {
      body.patient_id = Number(patientIdInput)
    }
    fetch(`/api/meets/${id}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
      .then((r) => r.json().then((data) => ({ status: r.status, data })))
      .then(({ status: st, data }) => {
        if (st === 200) {
          navigate("/meets")
          return
        }
        if (st === 400 && typeof data === "object") setFormError(data)
        else setError("Error al guardar")
      })
      .catch(() => setError("Error de conexión"))
      .finally(() => setSubmitLoading(false))
  }

  if (loading) return <p className="p-6 text-gray-600">Cargando…</p>
  if (error) return <p className="p-6 text-red-600">{error}</p>
  if (!meet) return null

  return (
    <div className="p-6 max-w-lg mx-auto">
      <h1 className="text-2xl font-semibold text-gray-800 mb-4">Editar cita #{meet.id}</h1>
      <p className="text-sm text-gray-600 mb-4">
        Terapeuta #{meet.therapist_id} · Fecha {meet.date} · Slot {meet.number}
      </p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Paciente (ID)</label>
          <input
            type="number"
            value={patientIdInput}
            onChange={(e) => setPatientIdInput(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2"
            placeholder="ID de paciente o vacío para dejar libre"
          />
          {meet.patient_name && (
            <p className="text-xs text-gray-500 mt-1">Actual: {meet.patient_name}</p>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Estado</label>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2"
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
        {formError.status && (
          <p className="text-red-600 text-sm mt-1">{formError.status[0]}</p>
        )}
        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={submitLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {submitLoading ? "Guardando…" : "Guardar"}
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

