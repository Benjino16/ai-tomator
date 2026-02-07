import {useState} from "react";
import {useNavigate} from "react-router-dom";
import { LoginAPI } from "../../api/login.ts";

export default function LoginPage() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        LoginAPI.login(username, password).then((result) => {
            if (result) {
                navigate("/")
            }
        }).catch((error) => {
            console.log(error);
            alert(error);
        })
    }

    return (
        <section>
            <h2>Login</h2>
            <form onSubmit={handleSubmit}>
                <label>Username</label>
                <input
                    type="text"
                    value={username}
                    minLength={3}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <label>Password</label>
                <input
                    type="password"
                    value={password}
                    minLength={6}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button type="submit">Login</button>
            </form>
        </section>
    );
}
