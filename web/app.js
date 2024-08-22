let width = 800;
let height = 600;

function showStats(stats, velocityStats) {
  // Show velocity
  const element = document.getElementById('velocity-stats').content.cloneNode(true);
  element.querySelector('.estimated').textContent = velocityStats.estimated_done_date;
  element.querySelector('.velocity').textContent = new Number(velocityStats.done_per_day).toFixed(2);
  document.getElementsByTagName('body')[0].prepend(element);

  const statTemplate = document.getElementById("stat").content;

  const statsToShow = stats && stats.length > 4 ? [stats[0], ...stats.slice(stats.length-3)] : stats;

  statsToShow.forEach((stat) => {
    const element = statTemplate.cloneNode(true);

    const checkedElement = element.querySelector('.checked');
    checkedElement.textContent = stat.checked_at;

    const todoElement = element.querySelector('.todo');
    todoElement.textContent = stat.todo_count;

    const doneElement = element.querySelector('.done');
    doneElement.textContent = stat.done_count;

    document.getElementsByTagName('body')[0].append(element);
  });
}

function init(jiraIssues) {
  var Engine = Matter.Engine,
      Render = Matter.Render,
      Runner = Matter.Runner,
      Bodies = Matter.Bodies,
      Composite = Matter.Composite;

  // create an engine
  var engine = Engine.create({ positionIterations: 40, velocityIterations: 40, constraintIterations: 40 });

  // create a renderer
  var render = Render.create({
      element: document.body,
      engine: engine,
      options: { width, height },
  });

  render.options.wireframes = false


  const poolWidth = width / 2;
  const poolHeight = height;
  const todoPoolParts = createPool(0, 0, poolWidth, poolHeight);

  const donePoolX = poolWidth + 5;
  const donePoolParts = createPool(donePoolX, 0, poolWidth, poolHeight);

  todoPoolBounds = Composite.bounds(todoPoolParts);
  donePoolBounds = Composite.bounds(donePoolParts);

  const todoIssues = jiraIssues.filter((issue) => ['To Do'].includes(issue.status))
  const inProgressIssues = jiraIssues.filter((issue) => ['In Progress'].includes(issue.status))
  const doneIssues = jiraIssues.filter((issue) => ['Done'].includes(issue.status))


  const delayBetweenIssue = 25;
  const todoIssuesDoneAt = 100 + todoIssues.length * delayBetweenIssue;

  todoIssues.forEach((issue, index) => {
    const timeout = 100 + index * delayBetweenIssue;
    setTimeout(() => Composite.add(engine.world, createIssue(issue, todoPoolBounds)), timeout);
  });
  inProgressIssues.forEach((issue, index) => {
    const timeout = todoIssuesDoneAt + index * delayBetweenIssue;
    setTimeout(() => Composite.add(engine.world, createIssue(issue, todoPoolBounds)), timeout);
  });
  doneIssues.forEach((issue, index) => {
    const timeout = 100 + index * delayBetweenIssue;
    setTimeout(() => Composite.add(engine.world, createIssue(issue, donePoolBounds)), timeout);
  });

  // add all of the bodies to the world
  Composite.add(engine.world, [todoPoolParts, donePoolParts]);

  // run the renderer
  Render.run(render);

  // create runner
  var runner = Runner.create();

  // run the engine
  Runner.run(runner, engine);
}

function createPool(x, y, width, height) {
  Bodies = Matter.Bodies
  const ground = Bodies.rectangle(x + width/2, height-10, width, 20, { isStatic: true });
  const leftWall = Bodies.rectangle(x + 10, height/2, 20, height, { isStatic: true });
  const rightWall = Bodies.rectangle(x + width-10, height/2, 20, height, { isStatic: true });
  leftWall.render.fillStyle = "blue";
  rightWall.render.fillStyle = "blue";
  ground.render.fillStyle = "blue";

  return Matter.Composite.create({ bodies: [ground, leftWall, rightWall] });
}

function getRandomInt(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min) + min); // The maximum is exclusive and the minimum is inclusive
}

function createIssue(issue, bounds) {
  const startHeigth = bounds.min.y + 50;
  const x = getRandomInt(bounds.min.x + 30, bounds.max.x - 30)
  const radius = issue.type === 'Bug' ? 10 : 15;
  const circle = Bodies.circle(x, startHeigth, radius);

  const priorityColorMap = {
    'Low': '#fdc500',
    'Medium': '#fd8c00',
    'High': '#dc0000',
    'Critical': '#780000'
  };

  const colorMap = {
    'To Do': 'pink',
    'In Progress': 'lightgreen',
    'Done': 'green'
  };
  circle.render.fillStyle =  issue.status == 'To Do' ? priorityColorMap[issue.priority] : colorMap[issue.status];
  circle.render.strokeStyle = "black";
  circle.render.lineWidth= "2";

  return circle;
}


