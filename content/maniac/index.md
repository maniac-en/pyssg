# ping-pong go code

[Back Home](/)

```
package main

import (
	"fmt"
	"time"
)

func pingPong(numPings int) {
	pings := make(chan struct{})
	pongs := make(chan struct{})
	go ponger(pings, pongs)
	pinger(pings, pongs, numPings)
}

func pinger(pings, pongs chan struct{}, numPings int) {
	go func() {
		sleepTime := 50 * time.Millisecond
		for i := 0; i < numPings; i++ {
			fmt.Printf("sending ping %v\n", i)
			pings <- struct{}{}
			time.Sleep(sleepTime)
			sleepTime *= 2
		}
		close(pings)
	}()
	i := 0
	for range pongs {
		fmt.Println("got pong", i)
		i++
	}
	fmt.Println("pongs done")
}

func ponger(pings, pongs chan struct{}) {
	i := 0
	for range pings {
		fmt.Printf("got ping %v, sending pong %v\n", i, i)
		pongs <- struct{}{}
		i++
	}
	fmt.Println("pings done")
	close(pongs)
}

func test(numPings int) {
	fmt.Println("Starting game...")
	pingPong(numPings)
	fmt.Println("===== Game over =====")
}

func main() {
	test(4)
	test(3)
	test(2)
}
```

## Solution discussion with boots

1. Original Code:

```
go ponger(pings, pongs)
go pinger(pings, pongs, numPings)
```

Outcome: Both `pinger` and `ponger` run concurrently. The pingPong function may
return before the game finishes, resulting in incomplete execution.

2. Removing go from `pinger` Only: (Solution)

```
go ponger(pings, pongs)
pinger(pings, pongs, numPings)
```

Outcome:

- `pinger` runs synchronously, ensuring pingPong waits for completion.
- `ponger` runs concurrently, sending pongs in response to pings.

> Result: The function only returns after all pings and pongs are processed,
> ensuring complete execution.

3. Removing go from `ponger` Only:

```
ponger(pings, pongs)
go pinger(pings, pongs, numPings)
```

Outcome:

- `ponger` runs synchronously and waits for pings.
- `pinger` never starts because pingPong is blocked on the synchronous ponger.

> Result: Deadlock. `ponger` waits indefinitely for pings that are never sent.

4. Removing go from Both:

```
ponger(pings, pongs)
pinger(pings, pongs, numPings)
```

Outcome:

- Both `ponger` and `pinger` run synchronously.
- pingPong is blocked on ponger, so `pinger` doesn't run.

> Result: Deadlock. Both functions block each other, waiting for communication
> that never happens.

### Summary Table

#### go ponger; go pinger

- Pinger -> Concurrent (goroutine)
- Ponger -> Concurrent (goroutine)
- Result -> Incomplete execution (may return early)

#### go ponger; pinger

- Pinger -> Synchronous (main flow)
- Ponger -> Concurrent (goroutine)
- Result -> Complete execution, hence this is the solution!

#### ponger; go pinger

- Pinger -> Synchronous (blocks main flow)
- Ponger -> Concurrent (never starts)
- Result -> Deadlock

#### ponger; pinger

- Pinger -> Synchronous (blocks main flow)
- Ponger -> Synchronous
- Result -> Deadlock

### Key Explanations:

- Concurrent (goroutine): The function runs concurrently in a new goroutine.
- Synchronous (main flow): The function runs as part of the main execution flow, blocking further progress until it completes.
- Synchronous (blocks main flow): The function runs in the main flow and causes deadlock by waiting indefinitely.
