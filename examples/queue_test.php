<?
$r = new Redis();

$r->connect("localhost", 4000);

for ($i = 0; $i < 100; $i++)
	$r->sadd("niki", "Item $i");

echo "Size " . $r->scard("niki") . "\n";

while($x = $r->spop("niki"))
	echo "$x\n";


