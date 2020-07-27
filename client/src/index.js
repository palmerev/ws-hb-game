import "babel-polyfill";
import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import {
    Button,
    Form,
    Alert,
} from "react-bootstrap";
import {
    BrowserRouter as Router,
    Route,
    Switch,
    NavLink,
    Redirect,
} from "react-router-dom";
import cookie from "react-cookies";
import Sockette from "sockette";
import CreateGamePage from './components/CreateGamePage';
import JoinGamePage from './components/JoinGamePage';
import GamePage from './components/GamePage';
import { msg } from './utils';
import './styles/index.scss';

const Nav = () => {
    return (
        <main>
          <nav>
            <ul>
              <li><NavLink to="/">Home</NavLink></li>
              <li><NavLink to="/create">Create</NavLink></li>
            </ul>
            </nav>
        </main>
    );
}

const HomePage = () => {
    return <div>
                <h1>Home</h1>
                <p>Welcome Home</p>
            </div>
}


class App extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            clientId: null,
            nickname: null,
            game: null,
        }
    }
    render() {
        return (
            <Router>
            <div className="container">
                <Nav />
                <Switch>
                    <Route path="/" exact component={HomePage} />
                    <Route path="/create" component={CreateGamePage} />
                    <Route path="/hb/game/:gameId" component={GamePage} />
                </Switch>
            </div>
            </Router>
        );
    }
}

const app = document.getElementById("app");

ReactDOM.render(<App />, app);
