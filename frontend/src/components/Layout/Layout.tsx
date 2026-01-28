import { Outlet } from "react-router-dom";
import Sidebar from "../Sidebar/Sidebar.tsx";
import styles from "./Layout.module.css";

export default function Layout() {
    return (
        <div className={styles.layout}>
            <Sidebar />
            <main>
                <Outlet />
            </main>
        </div>
    );
}
