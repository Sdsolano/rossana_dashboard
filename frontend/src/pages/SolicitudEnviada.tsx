import { Link, useLocation } from "react-router-dom"

export default function SolicitudEnviada() {
  const location = useLocation()
  const meet = (location.state as { meet?: { id?: number; date?: string } })?.meet

  return (
    <div className="max-w-xl mx-auto px-4 py-12 text-center">
      <div className="rounded-full bg-violet-100 w-16 h-16 flex items-center justify-center mx-auto mb-6 text-violet-600">
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Reserva confirmada</h1>
      <p className="text-gray-600 mb-6">
        Tu solicitud de terapia fue registrada. En breve te llegará un correo con los datos del turno
        {meet?.date && " y el link para la sesión"}.
      </p>
      <Link
        to="/"
        className="inline-flex px-5 py-2.5 rounded-lg bg-violet-600 text-white font-semibold hover:bg-violet-700"
      >
        Volver al inicio
      </Link>
    </div>
  )
}
