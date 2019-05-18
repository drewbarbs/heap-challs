Overview
--------

This directory has a solution to the
[SensePost Use-after-free challenge](https://sensepost.com/blog/2017/linux-heap-exploitation-intro-series-used-and-abused-use-after-free/),
and uses the `glibc_build.sh` script from
[how2heap](https://github.com/shellphish/how2heap) to run it with
glibc-2.25 (though it also works with glibc-2.29)

Running
-------

To run the solution with glibc-2.25 *and* debugging, do

```sh
$ docker build -t uaf .
$ docker run -it --rm --cap-add=SYS_PTRACE uaf
```

This compiles the challenge with debug symbols, and runs it in tmux
(one pane for solution script, another for GDB).


To run outside of docker and using whatever glibc is on your box, just
compile the challenge, and run the `chal.py` script with the
`NOPTRACE` argument. The script requires pwntools.

```sh
$ gcc -o uaf sensepost-uaf.c
$ ./chal.py NOPTRACE
```

Solution Sketch
-----------------

`strchunks` is initialized such that `strchunks[0]` is a pointer to a
buffer of size `SIZEOFMALLOCS` (an array of `char*`), the first entry
of that buffer is initialized to `flagmessage`.

We're given the address of the flag (just run the "Print" command).
Goal: set `*strchunks[0]` equal to flag address, then print that.

Steps (assuming glibc 2.25):
1. Print the address of the flag using the "Print contents" command
2. `free(strchunks[0])` (run the "free" command)

   All `malloc`'ated blocks in this program have a request size of
   `SIZEOFMALOCS` (`0x100 - 8`). As it happens, `strchunk[0]` is
   located right before the "top" chunk, so in pre-tcache malloc it is
   coalesced with `top` when it is `free`'d.

    `strchunks[0]` is not assigned `NULL` after it is `free`'d, so it
    is a dangling pointer.

3. Run the "allocate" command: `strchunks[1] = malloc(SIZEOFMALLOCS)`

   At this point, there are **no free chunks**, so a new chunk is
   split off of `av->top`. This ends up being a chunk **at the same
   address as `strchunks[0]`**

4. Write the address of the flag to `*strchunks[1]` (which is equal to
   `*strchunks[0]`) using the "Set contents" command
5. Print the flag using the "Print contents command" (use-after-free)

When we use glibc with tcache, the `free`d `strchunks[0]` ends up in
tcache, but is also immediately reused for the next allocation,
allowing us to alter the contents of `strchunks[0]` in the same way as
with glibc 2.25.
