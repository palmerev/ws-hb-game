import cookie from "react-cookies";
import React, {useEffect, useState} from "react";
import {
    Button,
    Form,
    Alert,
} from "react-bootstrap";
import Sockette from "sockette";

import { msg } from '../utils';


const GamePage = (props) => {
    let clientId = null;
    const gameId = props.match.params.gameId;
    const [game, setGame] = useState({});
    const [nickname, setNickname] = useState('');
    const [error, setError] = useState(null);
    const [pingInterval, setPingInterval] = useState(null);
    let [socket, setSocket] = useState(null);
    // if clientId cookie is undefined, this means that a player joined by visiting the url directly and needs to request, and be issued, a client id before they can officially join the game.
    const [wsError,setWSError] = useState(null);
    if (!gameId) {
        return <p>What? No game id?</p>;
    }
    const getPlayerList = () => {
        const cid = cookie.load('client_id')
        const players = (game && game.players ? game.players : []);
        if (players.length > 0) {
            const yourPlayer =
                players.filter(p => {
                    console.log("p.client_id:", p.client_id, "clientId", cid);
                    return p.client_id === cid
                }).length
                    ? players.filter(p => p.client_id === cid)[0]
                    : null;
            console.log("yourPlayer:", yourPlayer);
            return players.map(p => {
                const isYou = cid === p.client_id;
                return <div key={p.client_id}>{p.nickname} {isYou && '(You)'} connected with {p.client_id} {isYou && <Button>Edit nickname</Button>}</div>
            })
        }
    }

    const startSocket = () => {
        if (socket === null) {
            const ws = new Sockette('ws://dev.flatcow.space/ws/hbgame/' + gameId,
                {
                    timeout: 3000,
                    onopen: (event) => {
                        if (wsError !== null) {
                            setWSError(null);
                        }
                        ws.send(msg("preJoin", {gameId}));
                    },
                    onreconnect: (event) => {
                        console.log('reconnecting...', event.target.readyState, event)
                        if (wsError !== null) {
                            setWSError(null);
                        }
                        if (event.target.readyState === WebSocket.OPEN) {
                            ws.send(msg("preJoin", {gameId}));
                        }
                    },
                    onerror: (event) => {
                        console.log('error:', event);
                        setWSError(event);
                    },
                    onclose: (event) => {
                        console.log('connection closed:', event);
                    },
                    onmessage: (event) => {
                        const msg = JSON.parse(event.data);
                        if (msg.type === "pong") {
                            // console.log("received pong");
                        } else if (msg.type === "preJoin") {
                            // preJoin response should return entire game state
                            console.log('got preJoin message', msg);
                            setGame(msg.game);
                        } else {
                            console.log('received unknown message', msg);
                        }
                    },
                });
            setSocket(ws);
            if (socket !== null && pingInterval === null) {
                setPingInterval(setInterval(() => {
                    if (socket.readyState === WebSocket.OPEN) {
                        socket.send(msg("ping"));
                    }
                }, 60000))
            }
        }
    };

    useEffect(() => {
        clientId = cookie.load('client_id');
        if (typeof clientId === 'undefined' || clientId === null) {
            // request clientId
            console.log('fetching client id (join-game)');
            fetch(
                '/api/hb/join-game/' + gameId,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'same-origin',
                }
            )
                .then(async response => {
                    if (!response.ok) {
                        setError(response.statusText);
                        throw response;
                    } else {
                        return await response.json();
                    }
                })
                .then(res => {
                    console.log({joinGameResponse: res});
                    if (res.gameId) {
                        startSocket();
                    } else {
                        setError(`game id not found ${String(Object.entries(res))}`);
                    }
                })
                .catch(e => setError(e.toString()));
        } else {
            startSocket();
        }

        return () => {
            clearInterval(pingInterval);
        };
    }, []);

    const yourPlayer =
        game && game.players && game.players.length > 0
            ? game.players.filter(p => p.client_id === cookie.load('client_id'))[0]
            : null;
    return (
        <div>
            <h1>Game Page for {gameId}! Woo!</h1>
            <p>
                You are connected as {yourPlayer && yourPlayer.nickname || 'client'}
            </p>
            {game && getPlayerList()}
            {error && <div style={{color: 'red'}}>{error}</div>}


        </div>
    )
}

export default GamePage;