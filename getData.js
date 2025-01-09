// Login to https://suno.com/me
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
        // Generate random 5-character hash
        const hash = Math.random().toString(36).substring(2, 7);
        // Get UUID from the song's ID
        const uuid = x.value.id;
        // Format filename: lowercase, replace spaces with dashes, add id and hash
        const formattedTitle = `${title
          .toLowerCase()
          .replace(/\s+/g, "-")}-id-${hash}`;

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

        // Include original UUID filename in the description
        const fullDescription = `Original filename: ${uuid}.mp3\n\nPrompt:\n${description}`;

        // Always wrap description in quotes for consistency
        return `${formattedTitle}.mp3,${x.value.audio_url},"${fullDescription}"`;
      })
      .join("\n")
);
