import { useState } from 'react'
import '../styles/Sidebar.css'

function Sidebar({ onNavigate }) {
    const [sidebarOpen, setSidebarOpen] = useState(false)

    return (
        <div className="sidebar"> {/*Entire Component*/}
            <div className="sidebar-icon" onClick={()=> setSidebarOpen(!sidebarOpen)}> {/*Clickable hamburger icon*/}
                <div className="icon-bar"></div> {/*one of the 3 lines making up the icon */}
                <div className="icon-bar"></div>
                <div className="icon-bar"></div>
            </div>
            <nav className={`sidebar-nav ${sidebarOpen ? 'sidebar-nav-open' : ''}`}>
                <button className="sidebar-nav-item" onClick={() => onNavigate('previews')}>Previews</button>
                <button className="sidebar-nav-item" onClick={() => onNavigate('downloads')}>Downloads</button>
            </nav>
        </div>
    )
}

export default Sidebar