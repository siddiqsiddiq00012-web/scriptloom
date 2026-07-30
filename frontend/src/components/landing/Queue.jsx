import "./Queue.css";

function Queue() {
  const jobs = [
    {
      title: "YouTube Short",
      status: "Rendering",
      progress: 82,
    },
    {
      title: "Instagram Reel",
      status: "Queued",
      progress: 45,
    },
    {
      title: "TikTok Clip",
      status: "Waiting",
      progress: 18,
    },
  ];

  return (
    <div className="queue">
      <div className="queue__header">
        <h3>Processing Queue</h3>
      </div>

      <div className="queue__list">
        {jobs.map((job) => (
          <div className="queue__item" key={job.title}>

            <div className="queue__top">
              <span>{job.title}</span>
              <span>{job.progress}%</span>
            </div>

            <div className="queue__bar">
              <div
                className="queue__fill"
                style={{ width: `${job.progress}%` }}
              />
            </div>

            <div className="queue__status">
              {job.status}
            </div>

          </div>
        ))}
      </div>
    </div>
  );
}

export default Queue;