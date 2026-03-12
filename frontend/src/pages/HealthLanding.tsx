export default function HealthLanding() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-violet-50 via-white to-violet-100">
      <header className="border-b border-violet-900 bg-violet-950 text-violet-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-violet-400 flex items-center justify-center text-white font-bold text-sm">
              RD
            </div>
            <span className="font-semibold text-violet-50 text-lg tracking-wide">Rossana Salud</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm text-violet-100/80">
            <a href="#servicios" className="hover:text-white">Servicios</a>
            <a href="#como-funciona" className="hover:text-white">Cómo funciona</a>
            <a href="#testimonios" className="hover:text-white">Testimonios</a>
            <a href="#contacto" className="hover:text-white">Contacto</a>
          </nav>
          <div className="flex items-center gap-3 ml-auto">
            <a
              href="/login"
              className="px-4 py-1.5 rounded-full text-sm font-medium border border-violet-300 text-violet-50 hover:bg-violet-800"
            >
              Login
            </a>
            <a
              href="#contacto"
              className="px-4 py-1.5 rounded-full text-sm font-medium bg-emerald-400 text-violet-950 hover:bg-emerald-300"
            >
              Reservar demo
            </a>
          </div>
        </div>
      </header>

      <main>
        <section className="max-w-6xl mx-auto px-4 py-10 grid md:grid-cols-2 gap-10 items-center">
          <div>
            <p className="text-sm font-semibold text-violet-600 mb-2">Plataforma integral de bienestar</p>
            <h1 className="text-3xl sm:text-4xl font-bold text-violet-950 leading-tight mb-4">
              Tu salud emocional,<br />
              <span className="text-violet-600">en un solo lugar</span>
            </h1>
            <p className="text-violet-900/80 mb-6 text-sm sm:text-base">
              Rossana Salud conecta pacientes y terapeutas en una experiencia simple y humana:
              reservas online, recordatorios automáticos y un panel claro para seguir cada proceso.
            </p>
            <div className="flex flex-wrap gap-3 mb-6">
              <a
                href="/login"
                className="px-5 py-2.5 rounded-full text-sm font-medium bg-violet-600 text-white hover:bg-violet-700"
              >
                Entrar al panel
              </a>
              <a
                href="#servicios"
                className="px-5 py-2.5 rounded-full text-sm font-medium border border-violet-200 text-violet-800 hover:bg-violet-50"
              >
                Conocer más
              </a>
            </div>
            <div className="flex flex-wrap gap-4 text-xs text-violet-900/70">
              <div className="flex items-center gap-2">
                <span className="h-5 w-5 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs">✓</span>
                <span>Reservas online 24/7</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="h-5 w-5 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs">✓</span>
                <span>Recordatorios automáticos</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="h-5 w-5 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs">✓</span>
                <span>Panel para terapeutas y pacientes</span>
              </div>
            </div>
          </div>

          <div className="bg-white/80 rounded-2xl shadow-sm border border-violet-100 p-4 sm:p-6">
            <p className="text-xs font-medium text-violet-700 mb-3">Próximas sesiones</p>
            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between border border-violet-100 rounded-xl px-3 py-2 bg-violet-50/60">
                <div>
                  <p className="font-semibold text-violet-900">Sesión individual</p>
                  <p className="text-violet-800/80">Hoy · 18:00 hs · Online</p>
                </div>
                <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 text-[11px] font-medium">
                  Confirmada
                </span>
              </div>
              <div className="flex items-center justify-between border border-violet-100 rounded-xl px-3 py-2 bg-white">
                <div>
                  <p className="font-semibold text-violet-900">Sesión de seguimiento</p>
                  <p className="text-violet-800/80">Mañana · 10:30 hs · Presencial</p>
                </div>
                <span className="px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 text-[11px] font-medium">
                  Pendiente de pago
                </span>
              </div>
              <div className="flex items-center justify-between border border-violet-100 rounded-xl px-3 py-2 bg-white">
                <div>
                  <p className="font-semibold text-violet-900">Terapia de pareja</p>
                  <p className="text-violet-800/80">Jueves · 19:00 hs · Online</p>
                </div>
                <span className="px-2 py-0.5 rounded-full bg-violet-50 text-violet-700 text-[11px] font-medium">
                  En agenda
                </span>
              </div>
            </div>
            <p className="mt-4 text-[11px] text-violet-800/70">
              Vista simulada del panel administrativo. Los terapeutas gestionan su agenda y los pacientes
              reciben recordatorios automáticos por correo.
            </p>
          </div>
        </section>

        <section id="servicios" className="bg-white border-y border-violet-100">
          <div className="max-w-6xl mx-auto px-4 py-10">
            <h2 className="text-xl font-semibold text-violet-950 mb-6">Pensado para equipos de salud mental</h2>
            <div className="grid sm:grid-cols-3 gap-5 text-sm">
              <div className="bg-violet-50 rounded-xl p-4 border border-violet-100">
                <p className="text-xs font-semibold text-violet-700 mb-2">Para terapeutas</p>
                <p className="text-violet-900/80">
                  Agenda visual, bloqueo de días no laborables, gestión de pacientes y registro simple de pagos.
                </p>
              </div>
              <div className="bg-violet-50 rounded-xl p-4 border border-violet-100">
                <p className="text-xs font-semibold text-violet-700 mb-2">Para pacientes</p>
                <p className="text-violet-900/80">
                  Reserva online en pocos pasos, recordatorios por email y horario adaptado a su zona horaria.
                </p>
              </div>
              <div className="bg-violet-50 rounded-xl p-4 border border-violet-100">
                <p className="text-xs font-semibold text-violet-700 mb-2">Para la gestión</p>
                <p className="text-violet-900/80">
                  Reportes sencillos de citas y pagos, y un pequeño CMS para mantener actualizada la información del centro.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section id="como-funciona" className="max-w-6xl mx-auto px-4 py-10">
          <h2 className="text-xl font-semibold text-violet-950 mb-4">Cómo funciona la plataforma</h2>
          <ol className="space-y-3 text-sm text-violet-900/80">
            <li>
              <span className="font-semibold text-violet-800">1. Configura tu equipo.</span> Da de alta a los
              terapeutas y define su disponibilidad desde el panel.
            </li>
            <li>
              <span className="font-semibold text-violet-800">2. Abre la agenda a pacientes.</span> Tus pacientes
              reservan desde la web y reciben confirmación automática.
            </li>
            <li>
              <span className="font-semibold text-violet-800">3. Registra pagos y seguimiento.</span> Marca
              asistencia y pagos desde el panel y mantén todo en un solo lugar.
            </li>
          </ol>
        </section>

        <section id="testimonios" className="bg-violet-900 text-violet-50">
          <div className="max-w-6xl mx-auto px-4 py-10 grid md:grid-cols-2 gap-8 items-center">
            <div>
              <h2 className="text-xl font-semibold mb-4">Lo que dicen nuestros equipos</h2>
              <p className="text-sm text-violet-100/90 mb-4">
                “Unificamos todas las agendas en un solo lugar. Los pacientes reservan online y el equipo tiene
                claridad total sobre el día. Reducimos ausencias y duplicidad de registros.”
              </p>
              <p className="text-sm font-medium">Centro de Salud Mental Rossana</p>
            </div>
            <div className="border border-violet-700 rounded-2xl p-5 text-xs space-y-3 bg-violet-900/40">
              <p className="font-semibold text-violet-100">Indicadores clave</p>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <p className="text-2xl font-bold text-emerald-300">-35%</p>
                  <p className="text-violet-100/80">ausencias</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-emerald-300">+40%</p>
                  <p className="text-violet-100/80">citas online</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-emerald-300">1 lugar</p>
                  <p className="text-violet-100/80">para todo</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="contacto" className="max-w-6xl mx-auto px-4 py-10">
          <div className="bg-white rounded-2xl border border-violet-100 px-5 py-6 sm:px-8">
            <h2 className="text-xl font-semibold text-violet-950 mb-3">¿Te interesa la plataforma?</h2>
            <p className="text-sm text-violet-900/80 mb-4">
              Podemos adaptar la plataforma a tu centro de salud mental o consulta privada. Escríbenos y te
              mostramos una demo personalizada.
            </p>
            <p className="text-sm text-violet-900">
              Envíanos un correo a{" "}
              <a href="mailto:info@rossana.demo" className="text-violet-700 hover:text-violet-600 font-medium">
                info@rossana.demo
              </a>{" "}
              con el asunto <span className="font-semibold">“Quiero probar el dashboard”</span>.
            </p>
          </div>
        </section>
      </main>

      <footer className="border-t border-violet-100 bg-white/80">
        <div className="max-w-6xl mx-auto px-4 py-4 text-xs text-violet-900/70 flex flex-wrap items-center justify-between gap-2">
          <span>© {new Date().getFullYear()} Rossana Salud · Demo</span>
          <span>Construido sobre el dashboard Rossana</span>
        </div>
      </footer>
    </div>
  )
}

