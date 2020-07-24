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

import './styles/index.scss';

const Nav = () => {
    return (
        <main>
          <nav>
            <ul>
              <li><NavLink to="/">Home</NavLink></li>
              <li><NavLink to="/create">Create</NavLink></li>
              <li><NavLink to="/join">Join</NavLink></li>
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

const GamePage = (props) => {
    const gameId = props.match.params.gameId;
    const clientId = cookie.load('flatcowhbclient');
    // if clientId cookie is undefined, this means that a player joined by visiting the url directly and needs to request, and be issued, a client id before they can officially join the game.
    const [wsError,setWSError] = useState(null);
    if (!gameId) {
        return <p>What? No game id?</p>;
    }
    const url = '/api/ws/ping';
    useEffect(() => {
        if (typeof clientId === 'undefined') {
            // request clientId
        }
        let wsPing = new Sockette('ws://dev.flatcow.space/ws/ping',
            {
                timeout: 3000,
                onopen: (event) => {
                    if (wsError !== null) {
                        setWSError(null);
                    }
                    console.log('connection open:', event);
                },
                onreconnect: (event) => console.log('reconnecting...', event),
                onerror: (event) => {
                    console.log('error:', event);
                    setWSError(event);
                },
                onclose: (event) => {
                    console.log('connection closed:', event);
                },
                onmessage: (event) => {
                    console.log('message::data:', JSON.parse(event.data));
                    const msg = JSON.parse(event.data);
                    if (msg.type === "pong") {
                        console.log("received pong");
                    } else {
                        console.log('received unknown message');
                    }
                },
            });
        const pingInterval = setInterval(() => {
            wsPing.send(JSON.stringify({'ping': true}));
        }, 2000);

        return () => clearInterval(pingInterval);
    });
    // setup socket connection
    // recover from lost connection

    // fetch(
    //     url,
    //     {
    //         method: 'GET',
    //         headers: {
    //           'Accept': 'application/json',
    //           'Content-Type': 'application/json',
    //         },
    //         credentials: 'same-origin',
    //     }
    // )
    // .then(res => {
    //     // TODO: better error handling
    //     if (res.ok) {
    //         if (res.body.gameLocked) {
    //             throw new Error('Game locked!');
    //         }
    //     } else {
    //         throw res.statusText;
    //     }
    // });
    return (
        <div>
            <h1>Game Page for {gameId}! Woo!</h1>
            <p>Connected as client: {clientId}</p>
        </div>
    )
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
