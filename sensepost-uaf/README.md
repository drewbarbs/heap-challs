This directory has the solution to
[SensePost Use-after-free challenge](https://sensepost.com/blog/2017/linux-heap-exploitation-intro-series-used-and-abused-use-after-free/),
and uses the `glibc_build.sh` script from
[how2heap](https://github.com/shellphish/how2heap) to run it with glibc-2.25


Solution sketch:

`strchunks` is an array of `char**`, so each entry is a pointer to
`char*`. It's initialized such that `strchunks[0]` is a pointer to a
buffer of size `SIZEOFMALLOCS`, the first entry of that buffer is
initialized to `flagmessage`.

We're given the address of the flag (just run the "Print" command).
Goal: set `*strchunks[0]` equal to flag address, then print that.

Steps:
1. Print the address of the flag using the "Print contents" command
2. `free(strchunks[0])` (run the "free" command)

   All `malloc`'ated blocks in this program have a request size of
   `SIZEOFMALOCS` (`0x100 - 8`), which corresponds to a chunk too
   large for a fastbin/tcache/smallbin. As it happens, `strchunk[0]`
   is located right before the "top" chunk, so when it is `free`'d, it
   is coalesced with `top`.

    Conveniently, `strchunks[0]` is not assigned `NULL` after it is
    `free`'d, so it is a dangling pointer.

3. Run the "allocate" command: `strchunks[1] = malloc(SIZEOFMALLOCS)`

   At this point, there are **no free chunks**, so a new chunk is
   split off of `av->top`. This ends up being a chunk **at the same
   address as `strchunks[0]`**

4. Write the address of the flag to `*strchunks[1]` (which is equal to
   `*strchunks[0]`) using the "Set contents" command
5. Print the flag using the "Print contents command" (use-after-free)
