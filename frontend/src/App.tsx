import { BrowserRouter, Routes, Route, Link, useNavigate, useLocation } from "react-router-dom"
import "./App.css"
import { AuthProvider, useAuth } from "./context/AuthContext"
import Therapists from "./pages/Therapists"
import TherapistNew from "./pages/TherapistNew"
import TherapistEdit from "./pages/TherapistEdit"
import TherapistPassword from "./pages/TherapistPassword"
import Patients from "./pages/Patients"
import PatientNew from "./pages/PatientNew"
import PatientEdit from "./pages/PatientEdit"
import Meets from "./pages/Meets"
import MeetEdit from "./pages/MeetEdit"
import MeetBook from "./pages/MeetBook"
import SolicitarTerapia from "./pages/SolicitarTerapia"
import SolicitudEnviada from "./pages/SolicitudEnviada"
import Pays from "./pages/Pays"
import Pages from "./pages/Pages"
import PageNew from "./pages/PageNew"
import PageEdit from "./pages/PageEdit"
import PublicPage from "./pages/PublicPage"
import HealthLanding from "./pages/HealthLanding"
import Login from "./pages/Login"
import Panel from "./pages/Panel"
import PanelAvailability from "./pages/PanelAvailability"

function Nav() {
  const { isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()
  return (
    <nav className="border-b border-gray-200 bg-white px-6 py-3">
      <div className="max-w-5xl mx-auto flex flex-wrap items-center gap-4">
        <Link to="/" className="text-gray-600 hover:text-gray-900 font-medium">
          Inicio
        </Link>
        <Link to="/therapists" className="text-gray-600 hover:text-gray-900 font-medium">
          Terapeutas
        </Link>
        <Link to="/patients" className="text-gray-600 hover:text-gray-900 font-medium">
          Pacientes
        </Link>
        <Link to="/meets" className="text-gray-600 hover:text-gray-900 font-medium">
          Citas
        </Link>
        <Link to="/pays" className="text-gray-600 hover:text-gray-900 font-medium">
          Pagos
        </Link>
        <Link to="/pages" className="text-gray-600 hover:text-gray-900 font-medium">
          Contenido
        </Link>
        {isAuthenticated ? (
          <>
            <Link to="/panel" className="text-gray-600 hover:text-gray-900 font-medium">
              Panel
            </Link>
            <Link to="/panel/availability" className="text-gray-600 hover:text-gray-900 font-medium">
              Mi disponibilidad
            </Link>
            <button
              type="button"
              onClick={() => { logout(); navigate("/login"); }}
              className="text-gray-600 hover:text-gray-900 font-medium"
            >
              Cerrar sesión
            </button>
          </>
        ) : (
          <Link to="/login" className="text-gray-600 hover:text-gray-900 font-medium">
            Entrar
          </Link>
        )}
      </div>
    </nav>
  )
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    </AuthProvider>
  )
}

function AppLayout() {
  const location = useLocation()
  const isPublic = ["/", "/meets/book", "/solicitud-enviada"].includes(location.pathname)
  return (
    <>
      {!isPublic && <Nav />}
      <main>
        <Routes>
          <Route path="/" element={<HealthLanding />} />
          <Route path="/therapists" element={<Therapists />} />
          <Route path="/therapists/new" element={<TherapistNew />} />
          <Route path="/therapists/:id/edit" element={<TherapistEdit />} />
          <Route path="/therapists/:id/password" element={<TherapistPassword />} />
          <Route path="/patients" element={<Patients />} />
          <Route path="/patients/new" element={<PatientNew />} />
          <Route path="/patients/:id/edit" element={<PatientEdit />} />
          <Route path="/meets" element={<Meets />} />
          <Route path="/meets/new" element={<MeetBook />} />
          <Route path="/meets/book" element={<SolicitarTerapia />} />
          <Route path="/solicitud-enviada" element={<SolicitudEnviada />} />
          <Route path="/meets/:id/edit" element={<MeetEdit />} />
          <Route path="/pays" element={<Pays />} />
          <Route path="/pages" element={<Pages />} />
          <Route path="/pages/new" element={<PageNew />} />
          <Route path="/pages/:id/edit" element={<PageEdit />} />
          <Route path="/login" element={<Login />} />
          <Route path="/panel" element={<Panel />} />
          <Route path="/panel/availability" element={<PanelAvailability />} />
          <Route path="/public/:slug" element={<PublicPage />} />
        </Routes>
      </main>
    </>
  )
}

export default App
