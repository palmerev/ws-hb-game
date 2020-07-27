import React, { useState } from "react";
import {
    Button,
    Form,
    Alert,
} from "react-bootstrap";
import {Redirect} from "react-router-dom";


const JoinGamePage = () => {
    const [gameId, setGameId] = useState('');
    const [nickname, setNickname] = useState('');
    const [error, setError] = useState('');
    const [joinGameResponse, setJoinGameResponse] = useState(null);

    const joinGame = () => {
        fetch(
            '/api/hb/join-game',
            {
                method: 'POST',
                body: JSON.stringify({nickname, gameId}),
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
            }
        )
            .then(async response => {
                console.log({response});
                if (!response.ok) {
                    setError(response.statusText);
                    return response.statusText;
                } else {
                    return await response.json();
                }
            })
            .then(json => {
                console.log({joinGameResponse: json});
                if (json && !json.error) {
                    setJoinGameResponse(json);
                } else {
                    setError('game id not found');
                }
            })
            .catch(e => setError(e));
    };

    return (
        <div>
            <h1>Join Game</h1>
            <Form onSubmit={joinGame}>
                <Form.Group controlId="formNickname">
                    <Form.Label>Nickname</Form.Label>
                    <Form.Control
                        type="text"
                        placeholder="Enter nickname"
                        onChange={e => setNickname(e.target.value)}
                    />
                    <Form.Text className="text-muted">
                        Enter a nickname.
                    </Form.Text>
                </Form.Group>
                <Form.Group controlId="formGameId">
                    <Form.Label>Game ID</Form.Label>
                    <Form.Control
                        type="text"
                        onChange={e => setGameId(e.target.value)}
                    />
                    <Form.Text className="text-muted">
                        Enter a game ID.
                    </Form.Text>
                </Form.Group>
                <Button variant="primary" onClick={joinGame}>
                    Join
                </Button>
                {error && <Alert type="error">Failed to join game: {error}</Alert>}
            </Form>
            {joinGameResponse && <Redirect to={`/hb/game/${joinGameResponse.gameId}`} />}
        </div>
    );
}

export default JoinGamePage;