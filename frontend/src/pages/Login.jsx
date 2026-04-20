import { useState } from "react";
import { login, signup } from "../services/api";
import { useNavigate } from "react-router-dom";

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: 'Poppins', sans-serif;
    background: #f0f0f0;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .auth-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: #e8e8e8;
    font-family: 'Poppins', sans-serif;
    padding: 20px;
  }

  .auth-card {
    width: 750px;
    min-height: 480px;
    background: #fff;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.18);
    display: flex;
    overflow: hidden;
    position: relative;
  }

  /* ---- FORM SIDE ---- */
  .form-side {
    flex: 1;
    padding: 50px 45px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #fff;
    transition: all 0.5s ease;
  }

  .form-side h2 {
    font-size: 26px;
    font-weight: 700;
    color: #222;
    margin-bottom: 18px;
    letter-spacing: 0.5px;
  }

  .social-row {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
  }

  .social-btn {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    border: 1.5px solid #ddd;
    background: #fff;
    cursor: pointer;
    font-size: 14px;
    color: #555;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: border-color 0.2s, color 0.2s, transform 0.2s;
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
  }
  .social-btn:hover {
    border-color: #e85d5d;
    color: #e85d5d;
    transform: translateY(-2px);
  }

  .divider-text {
    font-size: 12px;
    color: #aaa;
    margin-bottom: 18px;
    letter-spacing: 0.3px;
  }

  .input-field {
    width: 100%;
    padding: 11px 16px;
    border: none;
    border-bottom: 1.5px solid #ddd;
    background: #f9f9f9;
    border-radius: 4px;
    font-size: 13.5px;
    color: #333;
    outline: none;
    margin-bottom: 14px;
    transition: border-color 0.2s, background 0.2s;
    font-family: 'Poppins', sans-serif;
  }
  .input-field:focus {
    border-color: #e85d5d;
    background: #fff;
  }
  .input-field::placeholder {
    color: #bbb;
  }

  .forgot-link {
    font-size: 12px;
    color: #aaa;
    margin-bottom: 22px;
    cursor: pointer;
    transition: color 0.2s;
    text-decoration: none;
    align-self: center;
  }
  .forgot-link:hover { color: #e85d5d; }

  .primary-btn {
    padding: 11px 44px;
    background: linear-gradient(135deg, #e85d5d, #ff8c6b);
    color: #fff;
    border: none;
    border-radius: 30px;
    font-size: 13.5px;
    font-weight: 700;
    letter-spacing: 1.5px;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    font-family: 'Poppins', sans-serif;
    text-transform: uppercase;
    box-shadow: 0 6px 20px rgba(232, 93, 93, 0.35);
  }
  .primary-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 28px rgba(232, 93, 93, 0.45);
  }
  .primary-btn:active { transform: translateY(0); }

  .error-text {
    color: #e85d5d;
    font-size: 12px;
    margin-bottom: 10px;
    align-self: flex-start;
  }

  /* ---- PANEL SIDE ---- */
  .panel-side {
    width: 310px;
    background: linear-gradient(145deg, #e85d5d 0%, #ff7a6b 60%, #ffaa80 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 50px 36px;
    text-align: center;
    transition: all 0.5s ease;
    position: relative;
    overflow: hidden;
  }

  .panel-side::before {
    content: '';
    position: absolute;
    width: 220px;
    height: 220px;
    border-radius: 50%;
    background: rgba(255,255,255,0.07);
    top: -60px;
    right: -60px;
  }
  .panel-side::after {
    content: '';
    position: absolute;
    width: 160px;
    height: 160px;
    border-radius: 50%;
    background: rgba(255,255,255,0.07);
    bottom: -40px;
    left: -40px;
  }

  .panel-side h3 {
    font-size: 24px;
    font-weight: 800;
    color: #fff;
    margin-bottom: 14px;
    line-height: 1.2;
    position: relative;
    z-index: 1;
  }

  .panel-side p {
    font-size: 13.5px;
    color: rgba(255,255,255,0.88);
    line-height: 1.65;
    margin-bottom: 30px;
    position: relative;
    z-index: 1;
  }

  .outline-btn {
    padding: 10px 36px;
    background: transparent;
    color: #fff;
    border: 2px solid #fff;
    border-radius: 30px;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.5px;
    cursor: pointer;
    transition: background 0.2s, color 0.2s, transform 0.2s;
    font-family: 'Poppins', sans-serif;
    text-transform: uppercase;
    position: relative;
    z-index: 1;
  }
  .outline-btn:hover {
    background: rgba(255,255,255,0.15);
    transform: translateY(-2px);
  }

  /* ---- SLIDE ANIMATION ---- */
  .auth-card.signup-mode .panel-side {
    order: -1;
    background: linear-gradient(145deg, #6b48ff 0%, #9c6bff 60%, #c79eff 100%);
  }
  .auth-card.signup-mode .panel-side::before,
  .auth-card.signup-mode .panel-side::after {
    background: rgba(255,255,255,0.07);
  }

  .slide-in {
    animation: slideIn 0.45s cubic-bezier(0.4,0,0.2,1);
  }

  @keyframes slideIn {
    from { opacity: 0; transform: translateX(30px); }
    to   { opacity: 1; transform: translateX(0); }
  }

  .slide-in-left {
    animation: slideInLeft 0.45s cubic-bezier(0.4,0,0.2,1);
  }

  @keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to   { opacity: 1; transform: translateX(0); }
  }

  @media (max-width: 640px) {
    .auth-card {
      flex-direction: column;
      width: 100%;
      max-width: 400px;
    }
    .panel-side {
      width: 100%;
      padding: 36px 28px;
      order: -1 !important;
    }
    .form-side {
      padding: 36px 28px;
    }
    .auth-card.signup-mode .panel-side {
      order: -1;
    }
  }
`;

export default function AuthPage() {
  const [mode, setMode] = useState("signin"); // "signin" | "signup"
  const [animKey, setAnimKey] = useState(0);

  const [signinData, setSigninData] = useState({ email: "", password: "" });
  const [signupData, setSignupData] = useState({ username: "", email: "", password: "" });
  const [errors, setErrors] = useState({});

  const switchMode = (next) => {
    setMode(next);
    setAnimKey((k) => k + 1);
    setErrors({});
  };

  const navigate = useNavigate();

  const validateSignin = () => {
    const e = {};
    if (!signinData.email) e.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(signinData.email)) e.email = "Invalid email";
    if (!signinData.password) e.password = "Password is required";
    return e;
  };

  const validateSignup = () => {
    const e = {};
    if (!signupData.username) e.username = "Username is required";
    else if (signupData.username.trim().length < 5) e.username = "Username must be at least 5 characters";
    if (!signupData.email) e.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(signupData.email)) e.email = "Invalid email";
    if (!signupData.password) e.password = "Password is required";
    else if (signupData.password.length < 8) e.password = "Password must be at least 8 characters";
    return e;
  };

  const handleSignin = async () => {
  const e = validateSignin();
  if (Object.keys(e).length) {
    setErrors(e);
    return;
  }

  try {
    const res = await login(signinData);

    if (res.access_token) {
      // 🔥 store token
      localStorage.setItem("token", res.access_token);

      // redirect
      navigate("/dashboard");
    } else {
      setErrors({ general: res.detail || "Login failed" });
    }
  } catch (err) {
    setErrors({ general: "Server error" });
  }
};

  const handleSignup = async () => {
  const e = validateSignup();
  if (Object.keys(e).length) {
    setErrors(e);
    return;
  }

  try {
    const res = await signup({
      username: signupData.username.trim(),
      email: signupData.email,
      password: signupData.password,
    });

    if (res?.id && res?.email) {
      // success → go to login
      switchMode("signin");
    } else {
      setErrors({ general: res.detail || "Signup failed" });
    }
  } catch (err) {
    setErrors({ general: err?.message || "Server error" });
  }
};

  const isSignup = mode === "signup";

  return (
    <>
      <style>{styles}</style>
      <div className="auth-wrapper">
        <div className={`auth-card ${isSignup ? "signup-mode" : ""}`}>

          {/* ---- FORM SIDE ---- */}
          <div className="form-side" key={animKey}
            style={{ animation: `${isSignup ? "slideIn" : "slideInLeft"} 0.45s cubic-bezier(0.4,0,0.2,1)` }}>

            {!isSignup ? (
              <>
                <h2>Sign In</h2>
                <div className="social-row">
                  <button className="social-btn">f</button>
                  <button className="social-btn">G+</button>
                  <button className="social-btn">in</button>
                </div>
                <p className="divider-text">or use your account</p>

                <input
                  className="input-field"
                  type="email"
                  placeholder="Email"
                  value={signinData.email}
                  onChange={(ev) => setSigninData({ ...signinData, email: ev.target.value })}
                />
                {errors.email && <span className="error-text">{errors.email}</span>}

                <input
                  className="input-field"
                  type="password"
                  placeholder="Password"
                  value={signinData.password}
                  onChange={(ev) => setSigninData({ ...signinData, password: ev.target.value })}
                />
                {errors.password && <span className="error-text">{errors.password}</span>}

                <span className="forgot-link">Forgot your password?</span>
                <button className="primary-btn" onClick={handleSignin}>Sign In</button>
              </>
            ) : (
              <>
                <h2>Create Account</h2>
                <div className="social-row">
                  <button className="social-btn">f</button>
                  <button className="social-btn">G+</button>
                  <button className="social-btn">in</button>
                </div>
                <p className="divider-text">or use your email for registration</p>

                <input
                  className="input-field"
                  type="text"
                  placeholder="Username"
                  value={signupData.username}
                  onChange={(ev) => setSignupData({ ...signupData, username: ev.target.value })}
                />
                {errors.username && <span className="error-text">{errors.username}</span>}

                <input
                  className="input-field"
                  type="email"
                  placeholder="Email"
                  value={signupData.email}
                  onChange={(ev) => setSignupData({ ...signupData, email: ev.target.value })}
                />
                {errors.email && <span className="error-text">{errors.email}</span>}

                <input
                  className="input-field"
                  type="password"
                  placeholder="Password"
                  value={signupData.password}
                  onChange={(ev) => setSignupData({ ...signupData, password: ev.target.value })}
                />
                {errors.password && <span className="error-text">{errors.password}</span>}

                <button className="primary-btn" onClick={handleSignup}>Sign Up</button>
              </>
            )}
          </div>

          {/* ---- PANEL SIDE ---- */}
          <div className="panel-side">
            {!isSignup ? (
              <>
                <h3>Hello, Friend!</h3>
                <p>Enter your personal details and start your journey with us</p>
                <button className="outline-btn" onClick={() => switchMode("signup")}>Sign Up</button>
              </>
            ) : (
              <>
                <h3>Welcome Back!</h3>
                <p>To keep connected with us please login with your personal info</p>
                <button className="outline-btn" onClick={() => switchMode("signin")}>Sign In</button>
              </>
            )}
          </div>

        </div>
      </div>
    </>
  );
}
