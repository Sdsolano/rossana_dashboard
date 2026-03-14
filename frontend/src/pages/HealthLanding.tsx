import { Link } from "react-router-dom"

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
        <span className="block text-[10px] sm:text-xs font-medium text-gray-500 uppercase tracking-wider">
          Sistema
        </span>
        <span className="block text-base sm:text-lg font-bold text-gray-900 tracking-tight">
          QMM Team
        </span>
      </div>
    </div>
  )
}

export default function HealthLanding() {
  const bookUrl = "/meets/book"
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-gray-100 bg-white">
        <div className="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-4">
          <Link to="/" className="flex items-center gap-2">
            <Logo />
          </Link>
          <nav className="flex items-center gap-6 text-sm font-medium text-gray-600">
            <a href="#inicio" className="hover:text-gray-900">
              Inicio
            </a>
            <a href="#como-funciona" className="hover:text-gray-900">
              Cómo funciona
            </a>
            <a href="#preguntas-frecuentes" className="hover:text-gray-900">
              Preguntas frecuentes
            </a>
            <Link
              to={bookUrl}
              className="px-4 py-2 rounded-lg bg-violet-600 text-white text-sm font-semibold hover:bg-violet-700 transition"
            >
              Solicita tu terapia
            </Link>
          </nav>
        </div>
      </header>

      {/* Promo banner */}
      <section className="bg-violet-600 text-white">
        <div className="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center justify-center gap-2 text-center text-sm">
          <span>
            ¿Querés solicitar tu primera terapia? Aprovechá un{" "}
            <strong>20% de descuento</strong> en tu primera terapia QMM.
          </span>
          <Link
            to={bookUrl}
            className="font-semibold underline underline-offset-2 hover:text-violet-100 whitespace-nowrap"
          >
            Solicitar ahora
          </Link>
        </div>
      </section>

      {/* Hero */}
      <section id="inicio" className="max-w-6xl mx-auto px-4 pt-12 pb-16">
        <div className="max-w-2xl">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-900 leading-tight mb-4">
            Solicita terapias de forma rápida, confiable y con terapeutas certificados
          </h1>
          <p className="text-gray-600 mb-8 text-base sm:text-lg">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Tempus diam pretium commodo
            diam. Lorem ipsum dolor sit.
          </p>
          <Link
            to={bookUrl}
            className="inline-flex px-6 py-3 rounded-lg bg-violet-600 text-white font-semibold hover:bg-violet-700 transition"
          >
            Solicitar una terapia
          </Link>
        </div>
        {/* Imagen / espacio para foto de terapeuta o ilustración */}
        <div className="mt-12 rounded-2xl overflow-hidden bg-gradient-to-b from-violet-100 to-violet-50 aspect-[16/10] max-h-[320px] flex items-end">
          <div
            className="w-full h-[70%] bg-cover bg-center bg-no-repeat"
            style={{
              backgroundImage: "url(https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=800&q=80)",
            }}
            title="Terapia"
          />
        </div>
      </section>

      {/* Cómo funciona */}
      <section id="como-funciona" className="bg-gray-50 border-y border-gray-100">
        <div className="max-w-6xl mx-auto px-4 py-14">
          <h2 className="text-2xl font-bold text-gray-900 mb-8">Cómo funciona</h2>
          <ol className="grid sm:grid-cols-3 gap-8 text-sm">
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-violet-600 text-white flex items-center justify-center font-bold">
                1
              </span>
              <div>
                <p className="font-semibold text-gray-900 mb-1">Elegí tu terapeuta</p>
                <p className="text-gray-600">
                  Revisá los profesionales disponibles y elegí el que mejor se adapte a vos.
                </p>
              </div>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-violet-600 text-white flex items-center justify-center font-bold">
                2
              </span>
              <div>
                <p className="font-semibold text-gray-900 mb-1">Reservá día y horario</p>
                <p className="text-gray-600">
                  Seleccioná una fecha y un turno disponible. Recibís confirmación al instante.
                </p>
              </div>
            </li>
            <li className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-violet-600 text-white flex items-center justify-center font-bold">
                3
              </span>
              <div>
                <p className="font-semibold text-gray-900 mb-1">Asistí a tu sesión</p>
                <p className="text-gray-600">
                  Presencial u online, según lo que ofrezca tu terapeuta. Nosotros te recordamos.
                </p>
              </div>
            </li>
          </ol>
          <div className="mt-10 text-center">
            <Link
              to={bookUrl}
              className="inline-flex px-5 py-2.5 rounded-lg bg-violet-600 text-white font-semibold text-sm hover:bg-violet-700 transition"
            >
              Solicitar una terapia
            </Link>
          </div>
        </div>
      </section>

      {/* Preguntas frecuentes */}
      <section id="preguntas-frecuentes" className="max-w-6xl mx-auto px-4 py-14">
        <h2 className="text-2xl font-bold text-gray-900 mb-8">Preguntas frecuentes</h2>
        <dl className="space-y-6 text-sm">
          <div>
            <dt className="font-semibold text-gray-900 mb-1">¿Cómo reservo una terapia?</dt>
            <dd className="text-gray-600">
              Hacé clic en &quot;Solicita tu terapia&quot;, elegí terapeuta, paciente (o creá uno), fecha y
              horario. Recibís confirmación por correo.
            </dd>
          </div>
          <div>
            <dt className="font-semibold text-gray-900 mb-1">¿Puedo elegir sesión presencial u online?</dt>
            <dd className="text-gray-600">
              Depende de cada terapeuta. En el proceso de reserva ves la disponibilidad y el tipo
              de sesión que ofrece.
            </dd>
          </div>
          <div>
            <dt className="font-semibold text-gray-900 mb-1">¿Hay descuento en la primera sesión?</dt>
            <dd className="text-gray-600">
              Sí, tenés un 20% de descuento en tu primera terapia QMM. Aprovechalo desde el botón
              &quot;Solicitar ahora&quot; del banner.
            </dd>
          </div>
        </dl>
      </section>

      {/* CTA final */}
      <section className="bg-violet-600 text-white">
        <div className="max-w-6xl mx-auto px-4 py-12 text-center">
          <h2 className="text-xl font-bold mb-2">¿Listo para tu primera sesión?</h2>
          <p className="text-violet-100 mb-6 text-sm">
            Agendá con terapeutas certificados de forma rápida y segura.
          </p>
          <Link
            to={bookUrl}
            className="inline-flex px-6 py-3 rounded-lg bg-white text-violet-600 font-semibold hover:bg-violet-50 transition"
          >
            Solicitar una terapia
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white">
        <div className="max-w-6xl mx-auto px-4 py-6 flex flex-wrap items-center justify-between gap-4 text-sm text-gray-500">
          <div className="flex items-center gap-2">
            <Logo />
          </div>
          <span>© {new Date().getFullYear()} QMM Team</span>
        </div>
      </footer>
    </div>
  )
}
