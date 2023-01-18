import React, { useState } from "react";
import axios from "axios";
import { NavBar } from "../../components";
import "./register.css";

const Register = () => {
  const validateEmail = (value) =>
    /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(value);

  const [username, setUserName] = useState("");
  const [email, setEmail] = useState("");
  const [passwords, setPasswords] = useState([]);

  const handleOnSubmit = (event) => {
    event.preventDefault();

    const validEmail = validateEmail(email);
    const matchingPasswords = passwords[0] === passwords[1];
    if (validEmail && matchingPasswords) {
      console.log("will try posting now!");
      axios({
        method: "post",
        url: "http://127.0.0.1:8000/userProfile/",
        data: {
          username,
          password: passwords[0],
          email,
          first_name: "",
          last_name: "",
        },
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then(function (response) {
          event.preventDefault();
          window.location.replace("http://127.0.0.1:3000");
          console.log(response);
        })
        .catch(function (error) {
          alert("Credentials already exist.");
          console.log(error);
        });
    } else {
      console.log("invalid!");
      if (!validEmail) {
        alert("Wrong email format");
      } else {
        alert("Passwords don't match");
      }
    }
  };

  return (
    <>
      <div>
        <NavBar />
      </div>
      <div className="registercontent"></div>
      <div className="registercontent">
        <form onSubmit={handleOnSubmit}>
          <p className="formtitle">Create an account</p>
          <div>
            <input
              className="namefield small"
              type="text"
              name="username"
              style={{ backgroundColor: "#d9d9d9" }}
              placeholder="Username"
              value={username}
              onChange={(event) => setUserName(event.target.value)}
              required
              minLength={5}
              maxLength={16}
            />
            *
          </div>
          <div>
            <input
              className="namefield small"
              type="text"
              name="fname"
              style={{ backgroundColor: "#d9d9d9" }}
              placeholder="First Name"
            />
            <input
              className="namefield small"
              type="text"
              name="lname"
              style={{ backgroundColor: "#d9d9d9" }}
              placeholder="Last Name"
            />
          </div>
          <div>
            <input
              type="password"
              name="password"
              className="small"
              style={{ backgroundColor: "#d9d9d9" }}
              placeholder="Password"
              value={passwords[0]}
              onChange={(event) =>
                setPasswords([event.target.value, passwords[1]])
              }
              required
              minLength={8}
              maxLength={15}
            />
            *
            <input
              type="password"
              name="cpassword"
              style={{ backgroundColor: "#d9d9d9" }}
              value={passwords[1]}
              onChange={(event) =>
                setPasswords([passwords[0], event.target.value])
              }
              placeholder="Confirm Password"
              className="small"
              required
              minLength={8}
              maxLength={15}
            />
            *
          </div>
          <input
            className="email small"
            type="text"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            name="email"
            style={{ backgroundColor: "#d9d9d9" }}
            placeholder="E-mail"
            required
          />
          *
          <input
            className="register"
            type="submit"
            value="Register"
            style={{ backgroundColor: "#d9d9d9", color: "#373B44" }}
          />
        </form>
      </div>
    </>
  );
};

export default Register;