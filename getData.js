// login to https://suno.com/me
copy(
  "song_name,song_url,song_prompt\n" +
    [
      ...$('[role="grid"]')[
        Object.keys($('[role="grid"]')).filter((x) =>
          x.startsWith("__reactProps")
        )[0]
      ].children[0].props.values[0][1].collection,
    ]
      .filter((x) => x.value.audio_url)
      .map((x) => {
        const title = x.value.title.trim() || x.value.id;
        // Format filename: lowercase, replace spaces with dashes
        const formattedTitle = title.toLowerCase().replace(/\s+/g, "-");

        // Find the description from the DOM using the song ID
        const songElement = document.querySelector(
          `[data-clip-id="${x.value.id}"]`
        );
        const descriptionSpan = Array.from(
          songElement.querySelectorAll("span[title]")
        ).find((span) => span.textContent.trim().length > 50);
        const description = descriptionSpan
          ? descriptionSpan.getAttribute("title")
          : "";

        // Always wrap description in quotes for consistency
        return `${formattedTitle}.mp3,${x.value.audio_url},"${description}"`;
      })
      .join("\n")
);
